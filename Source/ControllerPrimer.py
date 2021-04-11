# The first half is just boiler-plate stuff...

import pygame
import sys
import os
import time

BASE_TIME = 0
PRIMER = True
TRIAL_COUNT = 2
DEFAULT_BG_COLOUR = pygame.Color((30,30,30,100))
DEFAULT_FG_COLOUR = pygame.Color((212,212,212,100))

# Button Sequence Definitions
sequence_list = [
    ["A", "B", "X", "Y"],
    # ["A", "B", "Y", "X"],
    # ["A", "LB", "RB", "RSB"],
    # ["LB", "RB", "RT", "LT"],

    # ["RSB", "X", "RSB", "Y", "RSB", "B", "RSB", "A"],
    # ["LSB", "D-Left", "LSB", "D-Up", "LSB", "D-Right", "LSB", "D-Down"],
    # ["LSB", "LB", "LSB", "LT", "RSB", "RB", "RSB", "RT"],

    # ["D-Down", "L_up", "D-Up", "L_down", "LSB"],
    # ["L_left", "D-Right", "B", "RSB"],
    # ["LT", "LSB", "D-Right", "L_left"],
    # ["LT", "LSB", "D-Right", "L_right"],
    ["A", "B", "X", "Y", "LSB", "RSB", "LT", "RT", "RB", "LB", "D-Left", "D-Up", "D-Right", "D-Down"],
]

xbox_one_button_map = ["A", "B", "X", "Y", "LB", "RB", "View", "Menu", "LSB", "RSB" ]
xbox_one_hat_map = ["D-Left","D-Down","D-Right", "D-Up"]

class SceneBase:
    def __init__(self):
        self.next = self
        self.text = TextPrint()
    
    '''
    Handle inputs and modify class state variables.
    '''
    def ProcessInput(self, events, pressed_keys):
        print("uh-oh, you didn't override this in the child class")

    '''
    The decision logic of what to do with the state variables
    '''
    def Update(self):
        print("uh-oh, you didn't override this in the child class")

    '''
    Given the state variables and decisions made in ProcessInput and Update,
    this method draws the updated screen. 

    Limit updates to fill/blit, leave 'flip' to the object caller.
    '''
    def Render(self, screen):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene
    
    def Terminate(self):
        self.SwitchToScene(None)

# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint(object):
    def __init__(self, default_colour=DEFAULT_FG_COLOUR,top_margin=10,left_margin=10,
                                    line_height=35,font_size=40,tab_size=10):
    
        self.default_colour = default_colour
        self.top_margin = top_margin
        self.left_margin = left_margin
        self.line_height = line_height
        self.font_size = font_size
        self.tab_size = tab_size
        
        self.clear_screen()

    def println(self, screen, textString, colour = None, size=None):
        self.print(screen,textString,colour,size)
        self.newline()
    
    def print(self, screen, textString, colour = None, size=None):
        
        # Use default colour if no override provided
        if colour is None:
            _colour = pygame.Color(self.default_colour)
        else:
            _colour = pygame.Color(colour)

        # Use default size if no override provided
        if size is not None:
            font = pygame.font.Font(None, size)
        else:

            font = pygame.font.Font(None, self.font_size)

        # Need to make sure the text fits, otherwise will have to 
        # span multiple lines and update cursor 'location' accordingly.
        line = ""
        for word in textString.split():
            if self.x + font.size(line + word + " ")[0] > screen.get_size()[0]:
                lineBitmap = font.render(line, True, _colour)
                screen.blit(lineBitmap, (self.x, self.y))
                self.newline(size=size)
                line = ""
            line += word + " "
        
        # textBitmap = font.render(textString, True, _colour)
        lineBitmap = font.render(line, True, _colour)
        screen.blit(lineBitmap, (self.x, self.y))
        # screen.blit(textBitmap, (self.x, self.y))
        self.x += lineBitmap.get_width()


    def clear_screen(self):
        self.x = self.left_margin
        self.y = self.top_margin
    
    def newline(self, size=None):
        

        if size is not None:
            font = pygame.font.Font(None, size)
        else:
            font = pygame.font.Font(None, self.font_size)
        
        self.y += font.size("Tg")[1] # Gets the height of a line in the current font
        self.x = self.left_margin

    def indent(self):
        self.x += self.tab_size

    def unindent(self):
        self.x -= self.tab_size

class TrialLogger(object):
    def __init__(self):
        self.data = ""
        self.last_target = None

    def log_info(self, info_text):
        timestamp = time.time_ns() - BASE_TIME
        datetimestring = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())
        self.data += ",".join(["Info",info_text,str(timestamp),datetimestring,"\n"])

    def log_event(self, text, timestamp, target_button, target_match,seq_idx, trial_idx,button_idx):
        target_delta = ""
        if target_match:
            if self.last_target is None:
                self.last_target = timestamp
            else: 
                target_delta = str(timestamp - self.last_target)
                self.last_target = timestamp

        self.data += ",".join(map(str,[
                        "Event",
                        text,
                        timestamp,
                        target_button,
                        target_match,
                        "seq "+str(seq_idx),
                        "trial "+str(trial_idx),
                        "button "+str(button_idx),
                        target_delta,
                        "\n"
                    ]))
    
    def print_out(self):
        print(self.data)
    
    def write_out(self,seq_idx,trials_count):
        self.print_out()
        # Write out at the end of each sequence.
        filename = "_".join(map(str,[
                        "Seq",seq_idx,
                        "Trials",trials_count,
                        time.strftime("%Y-%m-%dT%H%M%S%z", time.localtime())]))
        
        filename += ".csv"
        with open(filename,'x') as out:
            out.write(self.data)



def run_game(width, height, fps, starting_scene):
   
    global BASE_TIME 
    BASE_TIME = time.time_ns()

    if getattr(sys, 'frozen', False): # PyInstaller adds this attribute
        # Running in a bundle
        CurrentPath = sys._MEIPASS
    else:
        # Running in normal Python environment
        CurrentPath = os.path.dirname(__file__)

    pygame.init()
    pygame.joystick.init() 
    pygame.display.set_caption("Xbox Input Study","Xbox Input Study")
    icon = pygame.image.load(os.path.join(CurrentPath,'icon_colour_1.png'))
    pygame.display.set_icon(icon)

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()
        
        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
            
            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)
        
        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)
        
        active_scene = active_scene.next
        
        pygame.display.flip()
        clock.tick(fps)
        
    pygame.quit()

# The rest is code where you implement your game using the Scenes model

class InstructionScene(SceneBase):
    # This screen greets the participant,
    # should check if the controller is connected,
    # and then waits on them for the study to begin.

    def __init__(self):
        SceneBase.__init__(self)
    
    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the 'study' GameScene when the user presses Enter
                # print(pygame.time.get_ticks())
                self.SwitchToScene(GameScene())
    
    def Update(self):
        pass
    
    def Render(self, screen):
        # Stops 

        self.text.clear_screen()
        screen.fill(DEFAULT_BG_COLOUR)
        self.text.println(screen, "Hello, thanks for agreeing to participate in my mini study!")
        self.text.newline()

        self.text.println(screen, "Please make sure your Xbox One controller is connected before running the study program.")
        self.text.newline()
        self.text.println(screen, "The following screens will ask you to press a series of buttons in the specified order.")
        self.text.newline()
        self.text.println(screen, "The next button to be pushed will be highlighted in yellow.")
        self.text.println(screen, "Buttons you've already pushed will be grayed out.")

        self.text.newline()
        self.text.newline()
        self.text.println(screen, "Press Enter to begin:")
        
    

class GameScene(SceneBase):
    def __init__(self, sequence_idx=0):
        SceneBase.__init__(self)
        self.seq_idx = sequence_idx # defines which button sequence is presented to the participant
        self.seq_len = len(sequence_list[sequence_idx])
        self.trial_idx = 0 # denotes the trial number of each button sequence (how many repeats)
        self.button_idx = 0 # Denotes which button is the target within the sequence
        self.trial_complete = False
        self.sequence_complete = False
        self.logger = TrialLogger()
        self.initial_frame = True
        self.target_hit = False
        
        # Yuck - maybe the only way around this is to store a full controller state object.
        # Too much for this right now though.
        self.LT_down = False
        self.RT_down = False
    
    def ProcessInput(self, events, pressed_keys):
        target_button = sequence_list[self.seq_idx][self.button_idx]
        self.target_hit = False # Resets with each event due to -f-elif structure
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                # Log the button and time
                time_to_log = time.time_ns() - BASE_TIME
                event_to_log = ",".join([xbox_one_button_map[event.button],"button-down"])
                

                if xbox_one_button_map[event.button] == target_button:
                    self.target_hit = True
                    self.button_idx += 1

                self.logger.log_event(event_to_log, time_to_log,target_button, self.target_hit,self.seq_idx,self.trial_idx,self.button_idx)

            # Everything that is a button. 
            elif event.type == pygame.JOYBUTTONUP:
                # Move to the next scene when the user pressed Enter
                time_to_log = time.time_ns() - BASE_TIME
                event_to_log = ",".join([xbox_one_button_map[event.button],"button-up"])
                self.logger.log_event(event_to_log, time_to_log,target_button, self.target_hit,self.seq_idx,self.trial_idx,self.button_idx)

            # Capture the DPAD inputs
            elif event.type ==  pygame.JOYHATMOTION:
                # hat value is a tuple (x,y) (x and y axes)
                # Where (-1, 0) is Left
                # and (-1, 1) is Left and Up

                # Due to the rocker nature of the controller the following
                # sequence of events is possible:
                # (-1, 0)
                # (-1, 1)
                # (-1, 0)
                # So both x and y should be checked for each event.

                # Checking 'if not zero' allows for a numeric shift
                # into 0-3 containing <L, vD, >R, ^U for a nicer mapping
                x, y = event.value 

                # Look at the DPAD x-axis
                if x != 0:
                    time_to_log = time.time_ns() - BASE_TIME
                    event_to_log = xbox_one_hat_map[x+1] + ",button-down"
                    
                    # Progress the index if target was correct.
                    if xbox_one_hat_map[x+1] == target_button:
                        self.target_hit = True
                        self.button_idx += 1
                    self.logger.log_event(event_to_log, time_to_log,target_button, self.target_hit,self.seq_idx,self.trial_idx,self.button_idx)
                # Look at the DPAD y-axis
                if y != 0:
                    time_to_log = time.time_ns() - BASE_TIME
                    event_to_log = xbox_one_hat_map[y+2] + ",button-down"

                    # Progress the index if target was correct.
                    if xbox_one_hat_map[y+2] == target_button:
                        self.target_hit = True
                        self.button_idx += 1
                    
                    self.logger.log_event(event_to_log, time_to_log,target_button, self.target_hit,self.seq_idx,self.trial_idx,self.button_idx)

                
            
            # Triggers and Joystick axes        
            elif event.type == pygame.JOYAXISMOTION:
                # Left Trigger is Axis 4
                # Right Trigger is Axis 5
                # pygame.CONTROLLER_AXIS_TRIGGERLEFT/RIGHT is available... 
                #   but undocumented at this time.

                # non-pressed state is approx -1.0 (slightly over, which is weird)
                # fully pressed is capped to 1.0
                # For now I'm assuming the 'click' threshold to be about 0

                if event.axis == pygame.CONTROLLER_AXIS_TRIGGERLEFT:

                    if event.value > 0 and not self.LT_down:
                        #This is the 'keydown' condition
                        self.LT_down = True
                        time_to_log = time.time_ns() - BASE_TIME
                        event_to_log = "LT,button-down"
                        
                        if "LT" == target_button:
                            self.target_hit = True
                            self.button_idx += 1
                        
                        self.logger.log_event(event_to_log, time_to_log,target_button, self.target_hit,self.seq_idx,self.trial_idx,self.button_idx)

                    elif event.value < 0 and self.LT_down:
                        #This is the 'keyup' condition
                        self.LT_down = False
                        time_to_log = time.time_ns() - BASE_TIME
                        event_to_log = "LT,button-up"
                    
                        self.logger.log_event(event_to_log, time_to_log,target_button, self.target_hit,self.seq_idx,self.trial_idx,self.button_idx)

                if event.axis == pygame.CONTROLLER_AXIS_TRIGGERRIGHT:

                    if event.value > 0 and not self.RT_down:
                        #This is the 'keydown' condition
                        self.RT_down = True
                        time_to_log = time.time_ns() - BASE_TIME
                        event_to_log = "RT,button-down"

                        if "RT" == target_button:
                            self.target_hit = True
                            self.button_idx += 1

                        self.logger.log_event(event_to_log, time_to_log,target_button, self.target_hit,self.seq_idx,self.trial_idx,self.button_idx)

                    elif event.value < 0 and self.RT_down:
                        #This is the 'keyup' condition
                        self.RT_down = False
                        time_to_log = time.time_ns() - BASE_TIME
                        event_to_log = "RT,button-up"
                        
                        self.logger.log_event(event_to_log, time_to_log,target_button, self.target_hit,self.seq_idx,self.trial_idx,self.button_idx)
        
    def Update(self):
        # This section controls the repetition and movement between 'scenes' 
        
        if self.initial_frame:
            self.initial_frame = False
            self.trial_start_time = time.time_ns()
            if PRIMER:
                self.logger.log_info("Primer Sequence")
            self.logger.log_info("Starting sequence {0}".format(self.seq_idx))
            self.logger.log_info("Sequence {0} Trial {1} BASETIME: {2}".format(
                                        self.seq_idx,self.trial_idx,BASE_TIME))

        
        # start the trial timer when the first button is pressed
        # idx+1 because increment occurs in ProcessInput())
        if self.target_hit and self.button_idx == 1:
            self.trial_start_time = time.time_ns()

        #Repeat sequence.
        # Once at the end of the sequence, repeat the trial.
        # Repeat sequence, increase trials count for that sequence.
        if self.button_idx == self.seq_len:
            self.button_idx = 0
            self.trial_complete = True
            trial_duration = time.time_ns() - self.trial_start_time
            self.logger.log_info("Sequence {0} Trial {1} complete in {2}".format(
                                        self.seq_idx,self.trial_idx,trial_duration))
            self.logger.log_info("Seq {0} Trial {1} duration:, {2}".format(
                                        self.seq_idx,self.trial_idx,trial_duration))
            self.trial_idx += 1

            
        

        #Next sequence or All done
        # After all trials of this sequence are complete:
        if self.trial_idx == TRIAL_COUNT:
            # Log the inputs
            self.logger.log_info("Sequence {0} complete (all {1} trials)".format(
                                        self.seq_idx, self.trial_idx))
            

            # Either this was the last sequence, so we're done.
            if self.seq_idx+1 == len(sequence_list):
                self.logger.log_info("Study Complete")
                self.SwitchToScene(FinishScene())
            else:
                # Or Move to the next sequence in the list
                self.SwitchToScene(GameScene(self.seq_idx + 1))

            if not PRIMER:
                self.logger.write_out(self.seq_idx,self.trial_idx)

    def Render(self, screen):
        # The game scene is just a blank blue screen
        self.text.clear_screen()
        
        screen.fill(DEFAULT_BG_COLOUR)
        
        self.text.println(screen,"Trial "+str(self.trial_idx+1)+" of "+str(TRIAL_COUNT), size=20, colour=(124,220,254,100))
        self.text.println(screen, "Push the following buttons in left-to-right sequence: ", size=20, colour="gray")

        for _idx,_button in enumerate(sequence_list[self.seq_idx]):
            if _idx == self.button_idx:
                font_colour = "yellow"
            elif _idx < self.button_idx:
                font_colour = (100,100,100)
            else:
                font_colour = "white"
    
            self.text.print(screen, _button + "  ", font_colour)
            
            # self.text.println(screen, str(sequence_list[self.seq_idx]), colour="white")


class FinishScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
    
    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter
                # print(pygame.time.get_ticks())
                pass
        
        
    def Update(self):
        pass
    
    def Render(self, screen):
        # The game scene is just a blank blue screen
        self.text.clear_screen()
        screen.fill(DEFAULT_BG_COLOUR)
        self.text.println(screen, "Thanks for participating!")
        self.text.newline()
        if PRIMER:
            self.text.println(screen, "You can now close this window and run the study.")
        else:
            self.text.println(screen, "You can now close this window and complete the exit survey.")

if __name__ == "__main__":
    # Need to init python before creating the InstructionScene() class 
    # or the font call to pygame will fail.
    pygame.init() 
    run_game(800, 800, 60, InstructionScene())