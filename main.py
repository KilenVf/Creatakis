from libs_var import*

from Medias.video import*
from Medias.functionsForMedias import*

from Uis.ExportWindow import*
from Uis.ImportWindow import*
from Uis.MainWindows import*
from Uis.PopUpWindows import*


if __name__ == "__main__":
    app = QApplication(sys.argv)

    FirstWindow = FirstWindowImport()
    if FirstWindow.exec_() == QDialog.Accepted:
        imported_video = import_de_videos()
    else :
        sys.exit()

    dialog = fenetre_OuiNon()
    ask_txt =(dialog.exec_() == QDialog.Accepted)

    

    if ask_txt:
        dialog_text = txt_contentWindow()
        if dialog_text.exec_() == QDialog.Accepted:
            txt_content = dialog_text.text_value
        else:
            txt_content = ''

    if txt_content:    
        txt_clip =  TextClip(
            text = txt_content,
            font_size = 100,
            color = 'white',
            size=(clip.w, 200)
        ).with_position("center").with_duration(5)

        
    else:
        video = clip
    
    title = txt_videotitle()
    ask_title = (title.exec_()==QDialog.Accepted)


    if ask_title == True:
        export_name = title.text_value
    
    export = export_medias()