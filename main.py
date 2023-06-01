from time import perf_counter
from io import BytesIO
from PIL import Image

import requests, concurrent.futures, colorama, datetime, os

colorama.init(True)

pl_map = Image.new(size=(12800, 12800), mode='RGB')

tile_id_to_x = lambda tile_id : (tile_id % 25 * 512)
tile_id_to_y = lambda tile_id : 12800 - ((int(tile_id * 0.04) * 512) + 512)

fin_tiles = 0

perf_counter_start = perf_counter()

def get_tile(tile_id):
    # Requests from PixelLand storage bucket
    tile_image_req = requests.get(f'https://storage.googleapis.com/pixelland_tiles/db9238ed-8377-4600-9b17-c0ecd06c3f23/{tile_id}.png')
    tile = Image.open(BytesIO(tile_image_req.content))
    
    # Pastes tile in full map
    pl_map.paste(tile, (tile_id_to_x(tile_id), tile_id_to_y(tile_id)))
    
    print(f'{colorama.Fore.WHITE}Tile{colorama.Fore.RESET} #{colorama.Fore.CYAN}{tile_id}\n', end='')

with concurrent.futures.ThreadPoolExecutor(max_workers=25) as pool:
    pool.map(get_tile, range(625))


print(f'{colorama.Fore.GREEN}Saving image...')

perf_counter_start_saving = perf_counter()

filename = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')
pl_map.save(f'plcam-{filename}.png','PNG')

perf_counter_end = perf_counter()

os.system('cls' if os.name == 'nt' else 'clear')

map_filesize = os.stat(f'plcam-{filename}.png').st_size

print(f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}Map Download Finished!')
print(f'''
{colorama.Fore.YELLOW}Time Taken (total){colorama.Fore.WHITE}: {colorama.Fore.CYAN}{perf_counter_end - perf_counter_start: >7.3f}{colorama.Fore.WHITE}s
{colorama.Fore.YELLOW}Time Loading Files{colorama.Fore.WHITE}: {colorama.Fore.CYAN}{perf_counter_start_saving - perf_counter_start: >7.3f}{colorama.Fore.WHITE}s
{colorama.Fore.YELLOW}Time Saving Image{colorama.Fore.WHITE}:  {colorama.Fore.CYAN}{perf_counter_end - perf_counter_start_saving: >7.3f}{colorama.Fore.WHITE}s

{colorama.Fore.YELLOW}Seconds/Tile (avg){colorama.Fore.WHITE}: {colorama.Fore.CYAN}{(perf_counter_start_saving - perf_counter_start) / 625: >7.3f}{colorama.Fore.WHITE}s

{colorama.Fore.YELLOW}Image Size{colorama.Fore.WHITE}:         {colorama.Fore.CYAN}{round(map_filesize / 1024): >7,}{colorama.Fore.WHITE}KB''')
