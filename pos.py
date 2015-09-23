import os
import sys
import random
import csv

from pygame.locals import *
from optparse import OptionParser
from VisionEgg import *
start_default_logging(); watch_exceptions()
from VisionEgg.Core import *
from VisionEgg.FlowControl import *
from VisionEgg.Textures import *
from VisionEgg.MoreStimuli import *
from VisionEgg.Text import *

###########

class Experiment:

    def __init__(self):
        self.subj,self.counter = self.parse()
        self.setup()
        self.make_order()


    def parse(self): #take commandline options
        parser = OptionParser()
        parser.add_option('-s','--subj',dest='subj')
        parser.add_option('-r','--run',dest='run')
        parser.add_option('-c','--counter',dest='counter')
        (options,arg) = parser.parse_args()
        four = ['1','2','3','4']
        if options.subj==None or options.counter not in four:
            print 'ERROR:\n-s  subj ID (any)\n-r  counter (1-5)'
            sys.exit()
        return options.subj, options.counter


    def setup(self):
        self.black = (0,0,0)
        self.white = (1,1,1)
        self.font_size = 60

        self.big_fix_t = 1.000
        self.word_t = 1.200
        self.fix_t = .550

        self.reset(0,'new')

        #screen
        self.screen = Screen(bgcolor=self.white,
                             size = (1024,640),
                             fullscreen = True)
        self.center = (self.screen.size[0]/2,self.screen.size[1]/2)
        #VisionEgg
        self.fix = FixationCross(position=self.center,
                                 size = (25,25))
        self.start = self.text('WAIT FOR TRIGGER')
        self.view=Viewport(screen=self.screen,
                           stimuli=[self.start])
        self.p=Presentation(viewports = [self.view],
                            handle_event_callbacks = [
                (pygame.locals.KEYDOWN, self.trigger),
                (pygame.locals.KEYDOWN, self.finish)],
                            go_duration = ('forever',))
   

    def make_order(self): #generate presentation order
        f = 'data/'+self.subj+'_data.csv'
        x = 1
        while os.path.isfile(f):
            x+=1
            f = 'data/'+self.subj+'-x'+str(x)+'_data.csv'
        self.data_file = open(f,'wb')
        self.wr = csv.writer(self.data_file, quoting = csv.QUOTE_MINIMAL)
        self.wr.writerow(['subj', 'run', 'counterbalancing', 'trial', 'word' , 'logfreq' , 'Cat' , 'length', 'run', 'start time'])
        self.order = []
        f = open('materials.csv','rU')
        items = [r for r in csv.reader(f) if r[-1]==self.run] #run number is last one there
        random.shuffle(items)
        self.d = {}
        for i in items:
            try: self.d[i[2]] += [i]
            except KeyError: self.d[i[2]] = [i]
        cbs = [line.strip().split() for line in open("cbs.txt").readlines()]
        counter_opts = {'1':cbs[0], '2':cbs[1], '3':cbs[2], '4':cbs[3]}
        for num, j in enumerate(counter_opts[self.counter]):
            if j == 'f': #fixation block
                self.order.append(['fix'])
            else: 
                self.order+= self.d[j] #self.make_block(self.d[j], num>10)


    # def make_block(self,categ, second_half): #if second half, return second half of block
    #     if second_half == True:
    #         return categ[8:]
    #     else: return categ[:8]

    def text(self,tx):
        return Text(anchor='center',
                    position=self.center,
                    font_size=self.font_size,
                    color=self.black,
                    text=tx.upper())


    def finish(self,event): #quit any time
        if event.key == pygame.locals.K_ESCAPE:
            self.screen.close()
            sys.exit()   


    def trigger(self,event): #start exp
        if event.unicode=='+':
            self.p.parameters.handle_event_callbacks = [
                (pygame.locals.KEYDOWN,self.finish)]
            self.p.parameters.go_duration = ('forever',)
            self.p.add_controller(self.view, 'stimuli', FunctionController(
                    during_go_func = self.switch))
            self.p.go() #start main exp loop


    def reset(self,t,k): #update vars after item in self.order
        last_start = t
        self.new = True
        self.current = None
        if k=='new':
            self.i, self.trial_n, self.ideal = 0,1,0
        else:
            self.i+=1
            if k=='trial':
                self.trial_n+=1
                self.ideal+=(self.word_t+self.fix_t)
            elif k=='fix':
                self.ideal+=self.big_fix_t


    def switch(self,t): #main exp timing loop
        if self.i<len(self.order):
            self.current = self.order[self.i]
            print "current", self.current
            if self.current[0] == 'fix': #fix block
                if t>(self.ideal+self.big_fix_t):
                    self.reset(t,'fix')
                return [self.fix]
            else: #trial
                if t<=(self.ideal+self.word_t):
                    if self.new: #word
                        #self.p.parameters.handle_event_callbacks = [
                        #    (pygame.locals.KEYDOWN,self.response),
                        #    (pygame.locals.KEYDOWN,self.finish)]
                        self.word = self.text(self.current[0])
                        self.onset = t
                    return [self.word]
                elif t<=(self.ideal+self.word_t+self.fix_t): #ISI
                    return []
                else: #record trial info
                    self.wr.writerow([self.subj,self.counter,self.trial_n] + self.current + [self.onset])
                    self.reset(t,'trial')
                    self.p.parameters.handle_event_callbacks = [
                        (pygame.locals.KEYDOWN,self.finish)]
                    return []
        else:
            print 'end time: ',t
            self.p.parameters.go_duration = (0,'seconds')
            self.data_file.close()
            return []

x = Experiment()


def Main():
    run = Experiment()
    run.p.go()
    
Main()
