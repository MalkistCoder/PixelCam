print('Loading...')

from time import perf_counter
from io import BytesIO
from PIL import Image

import requests, concurrent.futures, colorama, datetime, os, re

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

clear()

colorama.init(True)

tile_id_to_x = lambda tile_id, rows=25 : (tile_id % rows * 512)
tile_id_to_y = lambda tile_id, rows=25 : 512 * rows - ((int(tile_id / rows) * 512) + 512)

perf_counter_start = 0
perf_counter_start_saving = 0
perf_counter_end = 0

tiles_to_do = 0

pl_map = Image.new(size=(1, 1), mode='RGB')

def get_tile(tile_id: int, nether: bool=False):
    # Requests from PixelLand storage bucket
    dimension = 'db9238ed-8377-4600-9b17-c0ecd06c1111' if nether else 'db9238ed-8377-4600-9b17-c0ecd06c3f23'
    
    tile_image_req = requests.get(f'https://storage.googleapis.com/pixelland_tiles/{dimension}/{tile_id}.png')
    tile = Image.open(BytesIO(tile_image_req.content))
    
    # Pastes tile in full map
    pl_map.paste(tile, (tile_id_to_x(tile_id, 5 if nether else 25), tile_id_to_y(tile_id, 5 if nether else 25)))
    
    print(f'{colorama.Fore.WHITE}Tile{colorama.Fore.RESET} #{colorama.Fore.CYAN}{tile_id}\n', end='')

clear()

print(f'''{colorama.Fore.CYAN}╒══════════╕
{colorama.Fore.CYAN}│ {colorama.Fore.RED}Pixel{colorama.Fore.YELLOW}Cam {colorama.Fore.CYAN}│
{colorama.Fore.CYAN}╘══════════╛

Choose an option to begin.
  1. Download Overworld
  2. Download Nether
  3. Download Custom Dimension
''')

option = -1

while True:
    try:
        option = input('> ')
        if re.match('^[1-3]$', option):
            break
    except TypeError:
        pass

perf_counter_start = perf_counter()

if option == '3':
    tiles_to_do = 1
    
    print(f'{colorama.Fore.CYAN}Input custom dimension slug link (pixel.land/world/XXXXXXXX):')
    dimension_slug = input('> ')
    
    req = requests.post(
        'https://worlds.pixel.land/graphql',
        '{"operationName":"world","variables":{"slug":"' + dimension_slug + '"},"query":"query world($worldId: Uuid, $slug: String, $portalsFirst: Int, $portalsBefore: String) {\\n  world(worldId: $worldId, slug: $slug) {\\n    ...UserWorldsEdgeFragment\\n    node {\\n      portalsConnection(first: $portalsFirst, before: $portalsBefore) {\\n        edges {\\n          cursor\\n          node {\\n            id\\n            worldId\\n            x\\n            z\\n            destinationX\\n            destinationZ\\n            destinationWorldId\\n            __typename\\n          }\\n          __typename\\n        }\\n        pageInfo {\\n          ...PageInfoFragment\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment PageInfoFragment on PageInfo {\\n  hasNextPage\\n  hasPreviousPage\\n  __typename\\n}\\n\\nfragment UserWorldsEdgeFragment on UserWorldsEdge {\\n  cursor\\n  roles\\n  node {\\n    id\\n    createdAt\\n    slug\\n    name\\n    icon\\n    pixelsPerTileX\\n    pixelsPerTileZ\\n    tileCountX\\n    tileCountZ\\n    readAccess\\n    drawAccess\\n    backgroundColor\\n    backgroundImage\\n    baseColor\\n    __typename\\n  }\\n  __typename\\n}"}',
        headers={
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,id;q=0.8',
            'content-type': 'application/json',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
        }
    )
    
    world_id = req.json()['data']['world']['node']['id']
    
    tile_image_req = requests.get(f'https://storage.googleapis.com/pixelland_tiles/{world_id}/0.png')
    pl_map = Image.open(BytesIO(tile_image_req.content))
elif option == '2':
    tiles_to_do = 25
    
    pl_map = Image.new(size=(2560, 2560), mode='RGB')

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as pool:
        pool.map(lambda x: get_tile(x, True), range(25))
else:
    tiles_to_do = 625
    
    pl_map = Image.new(size=(12800, 12800), mode='RGB')

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as pool:
        pool.map(get_tile, range(625))

perf_counter_start_saving = perf_counter()

print(f'{colorama.Fore.GREEN}Saving image...')

filename_date = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')
filename = f'plcam-{filename_date}.png'
pl_map.save(filename,'PNG')

perf_counter_end = perf_counter()

map_filesize = os.stat(filename).st_size

print(f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}Map Download Finished!')
print(f'''
{colorama.Fore.YELLOW}Time Taken (total){colorama.Fore.WHITE}: {colorama.Fore.CYAN}{perf_counter_end - perf_counter_start: >7.3f}{colorama.Fore.WHITE}s
{colorama.Fore.YELLOW}Time Loading Files{colorama.Fore.WHITE}: {colorama.Fore.CYAN}{perf_counter_start_saving - perf_counter_start: >7.3f}{colorama.Fore.WHITE}s
{colorama.Fore.YELLOW}Time Saving Image{colorama.Fore.WHITE}:  {colorama.Fore.CYAN}{perf_counter_end - perf_counter_start_saving: >7.3f}{colorama.Fore.WHITE}s

{colorama.Fore.YELLOW}Seconds/Tile (avg){colorama.Fore.WHITE}: {colorama.Fore.CYAN}{(perf_counter_start_saving - perf_counter_start) / 625: >7.3f}{colorama.Fore.WHITE}s

{colorama.Fore.YELLOW}Filename{colorama.Fore.WHITE}:            {colorama.Fore.CYAN}{filename.split('.')[0]}{colorama.Fore.WHITE}.png
{colorama.Fore.YELLOW}Image Size{colorama.Fore.WHITE}:         {colorama.Fore.CYAN}{round(map_filesize / 1024): >7,}{colorama.Fore.WHITE}KB''')
