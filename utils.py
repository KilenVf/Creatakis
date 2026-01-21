# ============================================
# UTILS - FILE DIALOG
# ============================================

from tkinter import Tk, filedialog


def import_video():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename()

 