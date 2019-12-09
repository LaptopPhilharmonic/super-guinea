# Plytform tiles

import settings


class Animation:
    img_prefix = ""
    cycles_per_frame = 0
    frames = 1
    frame_speed = settings.fps
    cycle_count = 0
    current_frame_number = 0

    def __init__(self, img_prefix, frames, cycles_per_frame, loops):
        self.img_prefix = img_prefix
        self.cycles_per_frame = cycles_per_frame
        self.frames = frames
        self.current_frame = img_prefix + "1.png"
        self.loops = loops
        self.is_complete = False
        self.has_and_then_function = False
        self.and_then_function = None

    def update(self):
        if not self.is_complete:
            if self.current_frame_number > self.frames:
                self.is_complete = True
            else:
                self.cycle_count += 1
                if self.cycle_count > self.cycles_per_frame:
                    self.cycle_count = 0
                    self.current_frame_number += 1
                    if self.current_frame_number > self.frames:
                        if self.loops:
                            self.current_frame_number = 1
                    self.current_frame = self.img_prefix + str(self.current_frame_number) + ".png"
