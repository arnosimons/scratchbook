"""
`scratchbook.classes` implements the following classes:
`Curve`
    A scratch curve.
`Element`
    A scratch element.
`Scratch`
    A scratch made of one or more elements.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from pydub import AudioSegment

class MyLocator(matplotlib.ticker.AutoMinorLocator):
    def __init__(self, n=12):
        super().__init__(n=n)
                
matplotlib.ticker.AutoMinorLocator = MyLocator

slicetype = slice # to avoid name collision with "slice" scratch


### Helper Functions 
##############################################################################

def _findx(y, f, lower=0, upper=1, rounds=25, margin=0.0001):
    """
    Binary search for x given y using f in the domain from lower to upper.
    Assumes that f is defined between lower and upper and is continuous and 
    strictly monotonic
    """
    for i in range(1, rounds + 1):
        x = (upper + lower) / 2
        thisy = f(x)
        if abs(thisy - y) < margin:
            return x
        elif thisy < y:
            lower = x
        else:
            upper = x
    print("-> recursion limit reached at {i} rounds.")
    return x

def _pairwise(iterable): # make my own...
    import itertools 
    return itertools.pairwise(iterable)
 
def _milliseconds(sound, ms):
    """
    Rescales a sound to a given duration.
    """
    # https://stackoverflow.com/questions/51434897/how-to-change-audio-playback-speed-using-pydub
    if not ms > 0:
        raise ValueError("Amount must be greater than 0")
    if len(sound) == ms:
        return sound
    output = sound._spawn(sound.raw_data, overrides={
        "frame_rate": round((sound.frame_count() * 1000) / ms) # override framerate
    })
    return output.set_frame_rate(sound.frame_rate) # reset framerate


### Classes
##############################################################################

class Curve:
    """
    A class to control scratch curves and their rotation along the x-axis and/or
    y-axis
    """

    def __init__(self, f):
        """
        Parameters
        ----------
        f : function
            A function of x whose return values for 0 and 1 are 0 and 1, repectively.
        """
        self.forward = self.f = f
        self.backward =  self.b = lambda x: -f(x) + 1
        self.reverse = self.r = lambda x: f(1-x)
        self.inverse = self.i = lambda x: -f(1-x) + 1

class Element:
    """
    A class to define a scratch element
    """

    def __init__(self, curve, clicks=[], xflip=False, yflip=False, length=1, 
                             height=1, lift=0, color="k"):
        """
        Parameters
        ----------
        curve : Curve
            The scratch curve to be used by the scratch element.
        clicks: list
            A list of int or float values, all between 0 and 1. The relative
            x-locations of the crossfader clicks.
        xflip: bool
            Whether or not the curve should be flipped along the x-axis.
        yflip: bool
            Whether or not the curve should be flipped along the y-axis.
        length: int or float
            The length of the scratch element in number of beats.
        height: float
            A value between 0 and 1. The height of the scratch element in terms of
            relative sample length.
        lift: float
            A value between 0 and 1. The amount by the scratch element is lifted
            along the y-axis.
        """
        self.curve = curve
        self.clicks = [float(i) for i in clicks]
        self.xflip = xflip
        self.yflip = yflip
        self.length = float(length)
        self.height = float(height)
        self.lift = float(lift)
        self.color = color

    @property
    def ypos(self):
        """list: Combination of lift and height"""
        return [self.lift, self.height]

    @property
    def iclick(self):
        """bool: Whether element starts on a click"""
        return True if 0 in self.clicks else False

    @property
    def oclick(self):
        """bool: Whether element ends on a click"""
        return True if 1 in self.clicks else False

    @property
    def fclicks(self):
        """list: All clicks in between 0 and 1"""
        return [i for i in self.clicks if not i in [0, 1]]

    @property
    def fN(self):
        """int: Number of fclicks"""
        return len(self.fclicks)
    
    @property
    def forward(self):
        """bool: Whether element translates to forward playback"""
        return True if self.xflip == self.yflip else False

    def __truediv__(self, n):
        """Set the length of the element."""
        return Element(self.curve, self.clicks, self.xflip, self.yflip, n, 
                       self.height, self.lift, self.color)
    
    def __floordiv__(self, n):
        """Set the height of the element."""
        return Element(self.curve, self.clicks, self.xflip, self.yflip, self.length, 
                       n, self.lift, self.color)
    
    def __pow__(self, n):
        """Lift the element up or down the y-axis."""
        return Element(self.curve, self.clicks, self.xflip, self.yflip, self.length, 
                       self.height, n, self.color)
    
    def __neg__(self):
        """Flip the element along the y-axis."""
        return Element(self.curve, self.clicks, self.xflip, not self.yflip, self.length, 
                       self.height, self.lift, self.color)

    def __invert__(self):
        """Flip the element along the x-axis."""
        return Element(self.curve, [1 - c for c in self.clicks][::-1], not self.xflip, self.yflip, self.length, 
                       self.height, self.lift, self.color)

    @property
    def f(self):
        """Returns the active curve, given the flip setting"""
        if self.yflip:
            if self.xflip:
                return self.curve.inverse
            return self.curve.backward
        elif self.xflip:
            return self.curve.reverse
        return self.curve.forward

    def copy(self):
        """Returns a copy of the element"""
        return Element(self.curve, self.clicks, self.xflip, self.yflip, 
                                    self.length, self.height, self.lift, self.color)

    def audio(self, sample, grain=50, click_ms=60, fade_ms=10, 
              muting_color=None, muting_curve=None):
        """
        Calculate AudioSegment from element data

        Parameters
        ----------
        sample : AudioSegment
            The sample to be used
        grain : int
            The number of sample slices for each of which a new speed is calculated
        click_ms : int
            The duration of a click in milliseconds
        fade_ms: int
            Number of milliseconds by which clicks are faded in and out 
        """
        el = self
        backward = True if not el.forward else False # important, reused later when el has changed!!!
        if backward:
            el = el.copy()
            if el.yflip:
                el.xflip = True
            else:
                el.yflip = True
        old_duration = el.length * len(sample)
        if el.color == muting_color or el.curve == muting_curve:
            return AudioSegment.silent(duration=old_duration)
        start = int(len(sample) * el.lift)
        stop = int(len(sample) * (el.height + el.lift))
        sample = sample[start:stop]
        width = np.ceil(len(sample) / grain)
        slices = [sample[width * i: width * (i + 1)] for i in range(grain)] 
        ycuts = np.linspace(start=0, stop=1, num=grain + 1)
        xcuts = [_findx(y, el.f) for y in ycuts[1:-1]] # exclude first and last points, since their x are 0 and 1
        xcuts = [0] + xcuts + [1] # give them points back
        new_durations = [b - a for a, b in _pairwise(xcuts)]
        scratch = sum(_milliseconds(s, d * old_duration) 
                                for s, d in zip(slices, new_durations))
        if backward:
            scratch = scratch.reverse()
        fullclick = AudioSegment.silent(duration=click_ms)
        halfclick = AudioSegment.silent(duration=click_ms / 2)
        for i in [int(np.round(i * len(scratch))) for i in self.clicks]:
            if i == 0:
                scratch = halfclick + scratch[click_ms / 2:].fade_in(fade_ms)
            elif i == 1:
                scratch = scratch[:-(click_ms / 2)].fade_out(fade_ms) + halfclick
            else:
                scratch = sum([scratch[:i - (click_ms / 2)].fade_out(fade_ms),
                    fullclick,
                    scratch[i + (click_ms / 2):].fade_in(fade_ms)])
        return scratch


class Scratch:
    """
    A class to combine and transform scratch elements.
    """

    def __init__(self, elements):
        """
        Parameters
        ----------
        elements : list
            A list of Element objects.

        Methods
        ----------
        Note: all methods apply globally, i.e. in the same way to all elements.

        __add__ : self + other
            Concatenates two scratches.

        __mul__ : self * n
            Concatenates the scratch n times.

        __mod__ : self % n
            Shifts n elements from the end to the start of the scratch.

        ...

        """
        self.elements = list(elements)
        self.length = sum(i.length for i in self.elements)
        self.height = max(i.height + i.lift for i in self.elements)
        self.lift = min(i.lift for i in self.elements)
    
    def __getitem__(self, so):
        """Slice the scratch."""
        if isinstance(so, slicetype): # slicetype to avoid namespace conflict
            elements = self.elements[so]
        elif isinstance(so, int):
            elements = [self.elements[so]]
        else:
            message = f'Indexing must be of the form "[n]" or "[n:m]", where n and m are integers.'
            raise TypeError(message)
        return Scratch(elements)
    
    def __add__(self, other):
        """Add two scratches."""
        if not isinstance(other, Scratch):
            message = "A scratch can only be added to another scratch."
            raise TypeError(message)
        return Scratch(self.elements + other.elements)
    
    def __mul__(self, n):
        """Repeat a scratch n times."""
        if not isinstance(n, int) or (isinstance(n, int) and n < 1):
            message = "A scratch can only be multiplied by an integer > 0."
            raise ValueError(message)
        scratch = self
        for i in range(n-1):
            scratch += self
        return scratch
    
    def __mod__(self, n):
        """phase shift the scratch"""
        if not isinstance(n, int) or (
            isinstance(n, int) and n > len(self.elements)):
            message = "Phase shifting requires an integer smaller or equal to the number of elements. Here:" + str(len(self.elements))
            raise ValueError(message)
        return self[n:] + self[:n]

    def __truediv__(self, n):
        """Set the length of the scratch."""
        return Scratch([
            el / (el.length / self.length * n) for el in self.elements])

    def __floordiv__(self, n):
        """Set the height of the scratch."""
        return Scratch([
            (el // (el.height / self.height * n) ) 
            ** (el.lift / self.height * n)
            for el in self.elements])
    
    def __pow__(self, n):
        """Lift the scratch up or down the y-axis."""
        return Scratch([el ** (el.lift + n) for el in self.elements])

    def __neg__(self):
        """Flip the scratch along the y-axis."""
        return Scratch([-el ** (self.lift + 
            (self.height - (el.height + el.lift))) for el in self.elements])

    def __invert__(self):
        """Flip the scratch along the x-axis."""
        return Scratch([~el for el in self.elements][::-1])

    def audio(self, sample, bpm=90, instrumental=None, num_beats=4,
              muting_color=None, muting_curve=None):
        """
        Calculate AudioSegment from scratch data
        
        Parameters
        ----------
        bpm: int
            The number of beats per minute.
        sample: AudioSegment
            The scratch sample to be used.
        instrumental: AudioSegment
            The beat sample to be used.
        num_beats: int
            The length of the instrumental in number of beats.
            Only relevant if beat is provided
        """
        # ms_scratch = self.length / (bpm / 60) * 1000
        ms_scratch = self.length * 60000 / bpm
        scratch = _milliseconds(sum(
            i.audio(sample=sample, muting_color=muting_color, 
                muting_curve=muting_curve) 
            for i in self.elements), ms_scratch)
        if not instrumental:
            return scratch
        target_beats = int(np.ceil(self.length)) # num of beats to fit the scratch into
        ms_beat = len(instrumental) / num_beats
        if num_beats > target_beats:
            instrumental = instrumental[:(target_beats - num_beats) * ms_beat]
        elif num_beats < target_beats:
            # instrumental += instrumental[:(target_beats - num_beats) * ms_beat]
            instrumental = instrumental * (int(target_beats / num_beats)) + instrumental[:(target_beats % num_beats) * ms_beat]
        ms_instrumental = target_beats * 60000 / bpm
        return _milliseconds(instrumental, ms_instrumental).overlay(scratch)
        
    def TTM(self, ppb=100, size=2):
        """
        Transcribe the scratch using the Turntable Transcription Methodology
        (TTM).

        Parameters
        ----------
        ppb : int
                The resolution of the graph in terms of the number of points per beat.
        """
        beats = int(np.ceil(self.length))
        self.fig = Figure()
        self.fig.set_size_inches(beats * size, size)
        self.ax = self.fig.add_subplot(111)
        self.ax.cla()
        self.ax.grid(which='major', color='#2e2d2d', linewidth=0.8)
        self.ax.grid(which='minor', color='#787878', linestyle=':', linewidth=0.5)
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(1))
        self.ax.minorticks_on()
        margin = .1
        self.ax.set_xlim(0 - margin, beats + margin)
        self.ax.set_ylim(0 - margin, 1 + margin)
        self.ax.set_xlabel('Beats')
        self.ax.set_xticks(np.linspace(0, beats, beats + 1), [i for i in range(1,beats + 1)] + [""])
        self.ax.set_ylabel('Sample')
        self.ax.set_yticks([0,1], ["", ""])
        ax2 = self.ax.twinx()
        ax2.set_ylabel('Sample')
        ax2.set_yticks([0,1], ["", ""])
        strangescalar = .82
        for i in range(beats):
            if i % 4 == 0:
                self.ax.axvline(x=i, color='black')
            if not i % 2 == 0:
                self.ax.axvspan(i, 1 + i, facecolor='#e6e6e6', alpha=0.5,
                    ymin=1 - margin * strangescalar, 
                    ymax=margin * strangescalar)
            else:
                self.ax.axvspan(i, 1 + i, facecolor='#cccc', alpha=0.5, 
                    ymin=1 - margin * strangescalar, 
                    ymax=margin * strangescalar) 
        start = 0 
        for el in self.elements:
            f = el.curve.forward
            if el.yflip:
                f = el.curve.backward
                if el.xflip:
                    f = el.curve.inverse
            elif el.xflip:
                f = el.curve.reverse                
            num = round(el.length * ppb) + 1
            x_norm = np.linspace(start=0, stop=1, num=num) # normalized
            # y_crv = f(x_norm)
            y_crv = f(x_norm) * el.height + el.lift
            x_crv = np.linspace(start=start, stop=start+el.length, num=num) # scaled
            self.ax.plot(x_crv, y_crv, color=el.color, linewidth=3)
            for click in el.clicks:
                x_click = click * el.length + start
                y_click = np.interp(x_click, x_crv, y_crv) # get y from interpolation
                self.ax.plot(x_click, y_click, marker="o", markersize=8, 
                    markeredgecolor="black", markeredgewidth=1, 
                    markerfacecolor="white")
            start += el.length
        return self.fig

    def preview(self, ppb=50):
        """
        Returns a preview of the scratch in TTM

        Parameters
        ----------
        ppb : int
            The resolution of the graph in terms of the number of points per beat.
        """
        beats = int(np.ceil(self.length))
        self.fig = Figure()
        self.fig.set_size_inches(beats * 1, .75)
        self.ax = self.fig.add_subplot(111)
        self.ax.tick_params(left=False, right=False, labelleft=False, 
            labelbottom=False, bottom=False)
        self.ax.cla()
        start = 0 
        for el in self.elements:
            f = el.curve.forward
            if el.yflip:
                f = el.curve.backward
                if el.xflip:
                    f = el.curve.inverse
            elif el.xflip:
                f = el.curve.reverse                
            num = round(el.length * ppb) + 1
            x_norm = np.linspace(start=0, stop=1, num=num) # normalized
            y_crv = f(x_norm) * el.height + el.lift
            x_crv = np.linspace(start=start, stop=start+el.length, num=num) # scaled
            self.ax.plot(x_crv, y_crv, color=el.color, linewidth=3)
            for click in el.clicks:
                x_click = click * el.length + start
                y_click = np.interp(x_click, x_crv, y_crv) # get y from interpolation
                self.ax.plot(x_click, y_click, marker="o", markersize=5, 
                    markeredgecolor="black", markeredgewidth=1, 
                    markerfacecolor="white")
            start += el.length
            self.fig.patch.set_facecolor((0, 0, 0, 0.125))
            self.ax.margins(x=0)
            self.ax.set_axis_off()
        return self.fig