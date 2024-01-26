print('Loading...')

from time import perf_counter
from io import BytesIO
from PIL import Image

import requests, concurrent.futures, colorama, datetime, os

clear_terminal = lambda: os.system('cls' if os.name == 'nt' else 'clear')

clear_terminal()

colorama.init(True)

tile_id_to_x = lambda tile_id, rows=25 : (tile_id % rows * 512)
tile_id_to_y = lambda tile_id, rows=25 : 512 * rows - ((int(tile_id / rows) * 512) + 512)

tiles_to_do = 0

pl_map = Image.new(size=(1, 1), mode='RGB')

def overworld_range_id_to_tile_id(range_id: int):
    x = range_id % 25
    y = int(range_id / 25)
    
    return y * 128 + x + 6708 # Don't ask me, ask Will

def get_tile(range_id: int):
    tile_id = overworld_range_id_to_tile_id(range_id)
    
    tile_image_req = requests.get(f'https://images2.pixel.land/0x0/db9238ed-8377-4600-9b17-c0ecd06c3f23/97a548ca-4ecc-4776-96f4-f82af16137b0/{tile_id}.png')
    tile = Image.open(BytesIO(tile_image_req.content))
    
    # Pastes tile in full map
    pl_map.paste(tile, (tile_id_to_x(range_id), tile_id_to_y(range_id)))

clear_terminal()

print(f'''{colorama.Fore.CYAN}╒══════════╕
{colorama.Fore.CYAN}│ {colorama.Fore.RED}Pixel{colorama.Fore.YELLOW}Cam {colorama.Fore.CYAN}│
{colorama.Fore.CYAN}╘══════════╛

Press Enter to begin
''')
input()

perf_counter_start = perf_counter()

tiles_to_do = 625

pl_map = Image.new(size=(12800, 12800), mode='RGB')

print(f'Downloading tiles {colorama.Style.DIM}(this may take a while){colorama.Style.RESET_ALL}...')

with concurrent.futures.ThreadPoolExecutor(max_workers=25) as pool:
    pool.map(get_tile, range(625))

perf_counter_start_saving = perf_counter()

print(f'{colorama.Fore.GREEN}Saving image...')

filename_date = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')
filename = f'plcam-{filename_date}.png'
pl_map.save(filename,'PNG')

perf_counter_end = perf_counter()

map_filesize = os.stat(filename).st_size

# Performance info
print(f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}Map Download Finished!')
print(f'''
{colorama.Fore.YELLOW}Time Taken (total){colorama.Fore.WHITE}: {colorama.Fore.CYAN}{perf_counter_end - perf_counter_start: >7.3f}{colorama.Fore.WHITE}s
{colorama.Fore.YELLOW}Time Loading Files{colorama.Fore.WHITE}: {colorama.Fore.CYAN}{perf_counter_start_saving - perf_counter_start: >7.3f}{colorama.Fore.WHITE}s
{colorama.Fore.YELLOW}Time Saving Image{colorama.Fore.WHITE}:  {colorama.Fore.CYAN}{perf_counter_end - perf_counter_start_saving: >7.3f}{colorama.Fore.WHITE}s

{colorama.Fore.YELLOW}Seconds/Tile (avg){colorama.Fore.WHITE}: {colorama.Fore.CYAN}{(perf_counter_start_saving - perf_counter_start) / 625: >7.3f}{colorama.Fore.WHITE}s

{colorama.Fore.YELLOW}Filename{colorama.Fore.WHITE}:            {colorama.Fore.CYAN}{filename.split('.')[0]}{colorama.Fore.WHITE}.png
{colorama.Fore.YELLOW}Image Size{colorama.Fore.WHITE}:         {colorama.Fore.CYAN}{round(map_filesize / 1024): >7,}{colorama.Fore.WHITE}KB''')
