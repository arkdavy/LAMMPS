import matplotlib.pyplot as plt
import matplotlib.colors as mcol
import numpy as np

# plot setup
font_default=10
plt.rcParams.update({'font.size': font_default})
#plt.rcParams['text.latex.preview'] = True
#plt.rc('text', usetex=True)
plt.rc('font', family='serif')

markersize = 10
lineBaseColors = ['green', 'red', 'blue', 'k']
lineFadeColors = ['gold', 'slateblue', 'cyan', 'orange']

leftb = 0.12

def colorFader(c1,c2,mix=0,power=1): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mcol.to_rgb(c1))
    c2=np.array(mcol.to_rgb(c2))
    t=mix**power
    return mcol.to_hex((1-t)*c1 + t*c2)

def plotxy(x, y, style, ax, color='k', markersize = 0, label=''):
   ax.plot(x, y, style, color = color, markersize = markersize, 
                            markeredgecolor='k', label = label)



def initFigureRow(w, h, nrow, ncol, maxcores, title):

   fig = plt.figure(figsize=(w, h))

   vgap = 0.02
   hgap = 0.04
   botb = 0.12 - 0.01*nrow
   header_height = 0.3 + 0.1/nrow
   full_height = 0.65+ 0.05*nrow
   full_width = 0.8
   offset = 0.01

   ax01 = fig.add_axes([leftb, 1 - 0.5*header_height-0.035, full_width, 0.45*header_height])
   ax01.set_title(title)
   ax01.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=False,direction="in")
   ax01.tick_params(axis='y',which='both',labelright=True,left=True,right=True,direction="in")
   ax01.set_ylabel('time(s)')
   ax01.grid(visible=True)

   ax02 = fig.add_axes([leftb, 1 - header_height -0.03 , full_width, 0.45*header_height])
   ax02.tick_params(axis='x',which='both',bottom=False,top=True,direction="in")
   ax02.tick_params(axis='y',which='both',labelright=True,left=True,right=True,direction="in")
   ax02.set_xlabel('cores',labelpad=-0.5)
   ax02.set_ylabel('p. efficiency')
   ax02.grid(visible=True)

   axs = []
   for i in range(nrow):
    for j in range(ncol):

      width = (full_width-vgap*(ncol-1))/ncol 
      height = (1.04*full_height-header_height-hgap*(nrow-1))/nrow

      ax = fig.add_axes([leftb + width*j + vgap*j, botb + height*i + hgap*i, width, height])
      ax.tick_params(axis='x',which='both',bottom=True,top=True,direction="in")
      ax.tick_params(axis='y',which='both',left=True,right=True,direction="in")
      if (i==0 and j==0): 
          ax.set_ylabel('time (s)')
          ax.yaxis.set_label_coords(-0.15 , 0.5+0.7*nrow)
      if (i==1): ax.tick_params(axis='x',which='both',labelbottom=False,direction="in")
      if (j==0): ax.tick_params(axis='y',which='both',labelleft=True,labelright=False,left=True,right=True,direction="in")
      if (j==1): ax.tick_params(axis='y',which='both',labelleft=False,labelright=True,left=True,right=True,direction="in")
      ax.grid(visible=True)

      axs.append(ax)
   axs[-1].tick_params(axis='y',which='both',labelleft=False,labelright=True,left=True,right=True,direction="in")

   # here we just put a x-axis label
   
   ax1 = fig.add_axes([0.1, 0.01, full_width, 0.05])
   ax1.set_xlim([0,1])
   ax1.set_ylim([0,1])
   ax1.text(0.45,0.5,'cores')
   ax1.set_axis_off()
   return fig, [ax01,ax02], axs

def initFigure(w, h, maxcores, title):

   fig = plt.figure(figsize=(w, h))

   full_width = 0.8

   ax01 = fig.add_axes([leftb, 0.54, full_width, 0.38])
   ax01.set_title(title)
   ax01.tick_params(axis='x',which='both',bottom=True,top=True,labelbottom=False,direction="in")
   ax01.tick_params(axis='y',which='both',labelright=True,left=True,right=True,direction="in")
   ax01.set_ylabel('time(s)')
   ax01.grid(visible=True)

   ax02 = fig.add_axes([leftb, 0.14, full_width, 0.38])
   ax02.tick_params(axis='x',which='both',bottom=False,top=True,direction="in")
   ax02.tick_params(axis='y',which='both',labelright=True,left=True,right=True,direction="in")
   ax02.set_xlabel('cores')
   ax02.set_ylabel('p. efficiency')
   ax02.grid(visible=True)

   return fig, [ax01, ax02]
