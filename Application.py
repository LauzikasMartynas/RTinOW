import wx
from main import Build

# Panel in frame
class DisplayPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        size = parent.Size
        self.data = Build(size)
        self.SetSize((self.data.cam.image_width, self.data.cam.image_height))

        self.bitmap = wx.Bitmap.FromBuffer(self.data.cam.image_width, self.data.cam.image_height, self.data.image)
        self.img_ctrl = wx.StaticBitmap(self, bitmap=self.bitmap)

        box_sizer = wx.BoxSizer()
        box_sizer.Add(self.img_ctrl, -1, wx.ALL | wx.SHAPED, 5)

        # self.Bind(wx.EVT_PAINT, self.OnDraw)
        self.SetSizer(box_sizer)
        self.Fit()
        self.Show()

# Frame in app
class Frame(wx.Frame):
    def __init__(self):
        # Create a window with a panel where widgets are placed
        super().__init__(parent=None, title='Renderer')

        # Set size of rendered image
        self.SetSize((800, 500))
        # Create a panel
        self.panel = DisplayPanel(self)
        self.Show()

# Main app
if __name__ == '__main__':
    app = wx.App(False)
    frame = Frame()
    app.MainLoop()
