import matplotlib.pyplot as plt
import numpy as np
import random


def draw_neural_net(ax, layer_sizes, *args):
    '''
    Draw a neural network cartoon using matplotilb.
    This function is adapted from https://gist.github.com/craffel/2d727968c3aaebd10359
    
    :usage:
        >>> fig = plt.figure(figsize=(12, 12))
        >>> draw_neural_net(fig.gca(), [4, 7, 2], p)
    
    :parameters:
        - ax : matplotlib.axes.AxesSubplot
            The axes on which to plot the cartoon (get e.g. by plt.gca())
        - layer_sizes : list of int
            List of layer sizes, including input and output dimensionality
        - p : percentage of neurons to be dropped in each hidden layer
    '''
    
    #define some figure parameters
    left = .1 # (float) The center of the leftmost node(s) will be placed here
    right = .9 # (float) The center of the rightmost node(s) will be placed here
    bottom = .1 # (float) The center of the bottommost node(s) will be placed here
    top = .9 # (float) The center of the topmost node(s) will be placed here

    n_layers = len(layer_sizes) + 1
    v_spacing = (top - bottom)/float(max(layer_sizes))
    h_spacing = (right - left)/float(len(layer_sizes))
    end_spacing = 0.75*min(h_spacing, v_spacing)
    
    if len(args)==1:
        p = args[0]
        droped_dict = {}
    
    # Nodes
    for n, layer_size in enumerate(layer_sizes + layer_sizes[-1:]):
        
        layer_top = v_spacing*(layer_size - 1)/2. + (top + bottom)/2.
        
        if len(args)==1:
            drops = int(np.ceil(layer_size * (1-p)))
            selected = random.sample(range(0, layer_size),drops)
            droped_dict[n] = selected
            
        for m in xrange(layer_size):
            if n==0:
                shade = np.random.uniform(0, 1)
                rect = plt.Rectangle((n*h_spacing + left - v_spacing/4., layer_top - m*v_spacing - v_spacing/4.),
                                     v_spacing/2., v_spacing/2., fc=str(shade), ec='k', zorder=4)
                ax.add_artist(rect)
            elif n==len(layer_sizes)-1:
                circle = plt.Circle((n*h_spacing + left, layer_top - m*v_spacing), v_spacing/4.,
                                    fc='#fc8d59', ec='k', zorder=4)
                ax.add_artist(circle)
            elif n == len(layer_sizes):
                triangle = plt.Polygon([[(n-1)*h_spacing + left + end_spacing, layer_top - (m - 0.125)*v_spacing],
                                        [(n-1)*h_spacing + left + end_spacing, layer_top - (m + 0.125)*v_spacing],
                                        [(n-1)*h_spacing + left + end_spacing + 0.25*v_spacing, layer_top - m*v_spacing]],
                                       fc='#fc8d59', ec='k', zorder=4)
                ax.add_artist(triangle)
            else:
                if len(args)==1:
                    if m in selected:
                        circle = plt.Circle((n*h_spacing + left, layer_top - m*v_spacing), v_spacing/4.,
                                            fc='#ffffbf', ec='k', zorder=4)
                    else:
                        circle = plt.Circle((n*h_spacing + left, layer_top - m*v_spacing), v_spacing/4.,
                                            fc='#91bfdb', ec='k', zorder=4)
                else:
                    circle = plt.Circle((n*h_spacing + left, layer_top - m*v_spacing), v_spacing/4., 
                                        fc='#91bfdb', ec='k', zorder=4)
                ax.add_artist(circle)
    
    # Edges
    for n, (layer_size_a, layer_size_b) in enumerate(zip(layer_sizes[:-1], layer_sizes[1:])):
        layer_top_a = v_spacing*(layer_size_a - 1)/2. + (top + bottom)/2.
        layer_top_b = v_spacing*(layer_size_b - 1)/2. + (top + bottom)/2.
        for m in xrange(layer_size_a):
            if len(args)==1:
                if n == 0 or m not in droped_dict[n]:
                    for o in xrange(layer_size_b):
                        if n+2 == len(layer_sizes) or o not in droped_dict[n+1]:
                            line = plt.Line2D([n*h_spacing + left, (n + 1)*h_spacing + left],
                                              [layer_top_a - m*v_spacing, layer_top_b - o*v_spacing], c='k')
                            ax.add_artist(line)
            else:
                for o in xrange(layer_size_b):
                    line = plt.Line2D([n*h_spacing + left, (n + 1)*h_spacing + left],
                                      [layer_top_a - m*v_spacing, layer_top_b - o*v_spacing], c='k')
                    ax.add_artist(line)
    
    n = len(layer_sizes) - 1
    for m in xrange(layer_sizes[-1]):
        layer_top = v_spacing*(layer_sizes[-1] - 1)/2. + (top + bottom)/2.
        line = plt.Line2D([n*h_spacing + left, n*h_spacing + left + end_spacing],
                          [layer_top - m*v_spacing, layer_top - m*v_spacing], c='k')
        ax.add_artist(line)

def draw_neural_net_fig(*args, **kw):
    fig = plt.figure(figsize=(12,12))
    ax = fig.gca()
    ax.axis('off')
    draw_neural_net(ax, *args, **kw)


if __name__ == "__main__":
    import sys
    draw_neural_net(*sys.argv)