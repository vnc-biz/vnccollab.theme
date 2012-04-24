from zope.interface import Interface, implements

class IAvatarUtil(Interface):
    '''
    Interface for Avatar Utility.

    It calculates the css style to use on an image tag to preserve its
    aspect ratio and its intended size at the same time.
    '''

    def style(image, desired_size):
        '''returns the width, height and css style so the given image has the
           desire size and preserve its aspect ratio.'''


class AvatarUtil:
    implements(IAvatarUtil)

    def style(self, image, desired_size):
        pad_top = pad_right = pad_bottom = pad_left = 0
        cw, ch = image.width, image.height
        dw, dh = desired_size

        if image is None:
            return ''

        nw = min(dw, int(1.0*cw*dh/ch))
        nh = min(dh, int(1.0*ch*dw/cw))

        pad_left   = int((dw-nw)/2)
        pad_right  = dw - nw -pad_left
        pad_top    = int((dh-nh)/2)
        pad_bottom = dh - nh - pad_top

        style = 'pad: {0}px {1}px {2}px {3}px'.format(
                pad_top, pad_right, pad_bottom, pad_left)
        return nw, nh, style
