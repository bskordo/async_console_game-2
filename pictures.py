
def read_file(file_path):
    with open(file_path) as f:
        return f.read()


def get_garbages():
	files = ['garbages/trash_large.txt', 'garbages/trash_small.txt', 'garbages/trash_xl.txt']
	garbages = [read_file(file)for file in files]
	return garbages


def get_frames():
	files = ['frames/rocket_frame_1.txt','frames/rocket_frame_2.txt']
	frames = (read_file(file) for file in files)
	return frames

def get_game_over_text():
	text = read_file('frames/game_over.txt')
	return text