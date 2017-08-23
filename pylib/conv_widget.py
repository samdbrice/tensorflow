import numpy as np
from scipy.ndimage import convolve
from skimage import color
from ipywidgets import IntSlider
from IPython.html import widgets
import matplotlib.pyplot as plt

class ConvWidget:
    
    @classmethod
    def iter_pixels(cls, image):
        """ Yield pixel position (row, column) and pixel intensity. """
        height, width = image.shape[:2]
        for i in range(height):
            for j in range(width):
                yield (i, j), image[i, j]
    
    @classmethod
    def imshow_pair(cls, image_pair, titles=('', ''), figsize=(10, 5), **kwargs):
        fig, axes = plt.subplots(ncols=2, figsize=figsize)
        for ax, img, label in zip(axes.ravel(), image_pair, titles):
            ax.imshow(img, **kwargs)
            ax.set_title(label)
    
    @classmethod
    def padding_for_kernel(cls, kernel):
        """ Return the amount of padding needed for each side of an image.

        For example, if the returned result is [1, 2], then this means an
        image should be padded with 1 extra row on top and bottom, and 2
        extra columns on the left and right.
        """
        # Slice to ignore RGB channels if they exist.
        image_shape = kernel.shape[:2]
        # We only handle kernels with odd dimensions so make sure that's true.
        # (The "center" pixel of an even number of pixels is arbitrary.)
        assert all((size % 2) == 1 for size in image_shape)
        return [(size - 1) // 2 for size in image_shape]
    
    @classmethod
    def add_padding(cls, image, kernel):
        h_pad, w_pad = cls.padding_for_kernel(kernel)
        return np.pad(image, ((h_pad, h_pad), (w_pad, w_pad)),
                      mode='constant', constant_values=0)
    
    @classmethod
    def remove_padding(cls, image, kernel):
        inner_region = []  # A 2D slice for grabbing the inner image region
        for pad in cls.padding_for_kernel(kernel):
            slice_i = slice(None) if pad == 0 else slice(pad, -pad)
            inner_region.append(slice_i)
        return image[inner_region]
    
    @classmethod
    def window_slice(cls, center, kernel):
        r, c = center
        r_pad, c_pad = cls.padding_for_kernel(kernel)
        # Slicing is (inclusive, exclusive) so add 1 to the stop value
        return [slice(r-r_pad, r+r_pad+1), slice(c-c_pad, c+c_pad+1)]
    
    @classmethod
    def apply_kernel(cls, center, kernel, original_image):
        image_patch = original_image[cls.window_slice(center, kernel)]
        # An element-wise multiplication followed by the sum
        return np.sum(kernel * image_patch)
    
    @classmethod
    def iter_kernel_labels(cls, image, kernel):
        """ Yield position and kernel labels for each pixel in the image.

        The kernel label-image has a 1 for everympixel "under" the kernel.
        Pixels not under the kernel are labeled as 0.

        Note that the mask is the same size as the input image.
        """
        original_image = image
        image = cls.add_padding(original_image, kernel)
        i_pad, j_pad = cls.padding_for_kernel(kernel)

        for (i, j), pixel in cls.iter_pixels(original_image):
            # Shift the center of the kernel to ignore padded border.
            i += i_pad
            j += j_pad
            mask = np.zeros(image.shape, dtype=int)  # Background = 0
            mask[cls.window_slice((i, j), kernel)] = 1   # Kernel = 1
            yield (i, j), mask
    
    @classmethod
    def visualize_kernel(cls, kernel_labels, image):
        """ Return a composite image, where 1's are yellow and 2's are red.

        See `iter_kernel_labels` for info on the meaning of 1 and 2.
        """
        return color.label2rgb(kernel_labels, image, bg_label=0,
                               colors=('yellow', 'red'))
    
    @classmethod
    def make_convolution_step_function(cls, image, kernel, **kwargs):
        # Initialize generator since we're only ever going to iterate over
        # a pixel once. The cached result is used, if we step back.
        gen_kernel_labels = cls.iter_kernel_labels(image, kernel)
        stride = image.shape[1]
        print stride

        image_cache = []
        image = cls.add_padding(image, kernel)

        def convolution_step(i_step):
            """ Plot original image and kernel-overlay next to filtered image.

            For a given step, check if it's in the image cache. If not
            calculate all necessary images, then plot the requested step.
            """

            # Create all images up to the current step, unless they're already
            # cached:
            
            while i_step >= len(image_cache):

                # For the first step (`i_step == 0`), the original image is
                # full of NaNs; after that we look in the cache, which stores
                # (`kernel_overlay`, `filtered`).
                filtered_prev = np.full_like(image, np.nan) if i_step == 0 else image_cache[-1][1]
                # We don't want to overwrite the previously filtered image:
                filtered = filtered_prev.copy()

                # Get the labels used to visualize the kernel
                center, kernel_labels = gen_kernel_labels.next()
                # Modify the pixel value at the kernel center
                filtered[center] = cls.apply_kernel(center, kernel, image)
                # Take the original image and overlay our kernel visualization
                kernel_overlay = cls.visualize_kernel(kernel_labels, image)
                # Save images for reuse.
                image_cache.append((kernel_overlay, filtered))

            # Remove padding we added to deal with boundary conditions
            # (Loop since each step has 2 images)
            image_pair = [cls.remove_padding(each, kernel)
                          for each in image_cache[i_step]]
            cls.imshow_pair(image_pair, cmap='gray', **kwargs)
            center = (i_step / stride, i_step % stride)
            plt.sca(plt.gcf().axes[0])
            plt.plot([center[1]], [center[0]], 'ro')
            plt.show()

        return convolution_step  # <-- this is a function
    
    @classmethod
    def interactive_convolution_demo(cls, image, kernel, **kwargs):
        stepper = cls.make_convolution_step_function(image, kernel, **kwargs)
        step_slider = IntSlider(min=0, max=image.size-1, value=0)
        widgets.interact(stepper, i_step=step_slider)