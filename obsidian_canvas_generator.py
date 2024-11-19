import PySimpleGUI as sg
import json
import os
import requests
import subprocess

version = "1.0.0"

def generate_canvas(file_path, output_path):
    try:
        with open(file_path, 'r') as file:
            links = [line.strip() for line in file.readlines() if line.strip()]
            
        total_links = len(links)
        num_columns = math.ceil(math.sqrt(total_links))
        nodes = []
        x, y = 0, 0
        width, height = 540, 300
        padding = 50 

        for i, link in enumerate(links):
            node = {
                "id": f"node_{i}",
                "type": "text",
                "text": f"<iframe src=\"{link}\" allow=\"fullscreen\" allowfullscreen=\"\" style=\"height:100%;width:100%; aspect-ratio: 16 / 9; \"></iframe>",
                "x": x,
                "y": y,
                "width": width,
                "height": height
            }
            nodes.append(node)
            if (i + 1) % num_columns == 0:
                x = 0
                y += height + padding
            else:
                x += width + padding

        canvas_data = {
            "nodes": nodes,
            "edges": []
        }

        with open(output_path, 'w') as output_file:
            json.dump(canvas_data, output_file, indent=4)

        sg.popup("Success", f"Canvas generated: {output_path}")
    except Exception as e:
        sg.popup("Error", f"An error occurred: {e}")

def main():
    sg.theme('DarkBlue')
    layout = [
        [sg.Column([[sg.Button('Generate Source'), sg.Button('Build Script'), sg.Button('Check update')]], justification='center')],
        [sg.Input(key="-FILE-", enable_events=True, visible=False), sg.FileBrowse(file_types=(("Text Files", "*.txt"),)), sg.Text("Select a .txt file with links")],
        [sg.Input(key="-FOLDER-", enable_events=True, visible=False), sg.FolderBrowse(), sg.Text("Select the folder to save the canvas")],
        [sg.Text("Enter a name for the canvas file:"), sg.InputText(key="-FILENAME-", size=(25, 1))],
        [sg.Column([[sg.Button("Generate Canvas")]], justification='center')],
    ]

    window = sg.Window("Obsidian Canvas Generator " + version, layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'Generate Source':
            if download_source():
                sg.popup("Done")
            else:
                sg.popup("Web site does not exist or is not reachable")
                
        elif event == 'Build Script':
            if download_build_script():
                sg.popup("Done")
            else:
                sg.popup("Web site does not exist or is not reachable")
    
        elif event == 'Check update':
            response = requests.get("https://raw.githubusercontent.com/Scavix/links-to-obsidian-canvas/main/version.json")
            if response.status_code == 200:
                if response.json()["version"] != version:
                    if sg.popup_yes_no("New version available: " + response.json()["version"] + ". Do you want to update?", title="To update") == "Yes":
                        if download_both():
                            subprocess.run([r"auto_updater_build_script.bat"])
                            os.remove("obsidian_canvas_generator.py")
                            os.remove("auto_updater_build_script.bat")
                            os.remove("obsidian_canvas_generator.spec")
                            sg.popup("Done")
                            window.close()
                        else:
                            sg.popup("Web site does not exist or is not reachable")
                        break
                else:
                    sg.popup("No new version available, actual: " + response.json()["version"], title="Updated")
            else:
                sg.popup("Web site does not exist or is not reachable\n" + response.status_code+"\n"+response.reason+"\n"+response.text)

        elif event == "Generate Canvas":
            file_path = values["-FILE-"]
            folder_path = values["-FOLDER-"]
            filename = values["-FILENAME-"]

            if os.path.exists(file_path) and folder_path and filename:
                if not filename.endswith(".canvas"):
                    filename += ".canvas"
                output_path = os.path.join(folder_path, filename)
                generate_canvas(file_path, output_path)
            else:
                sg.popup("Error", "Please provide a valid .txt file, folder, and filename.")

    window.close()

def download_source():
    response = requests.get("https://raw.githubusercontent.com/Scavix/links-to-obsidian-canvas/main/obsidian_canvas_generator.py")
    if response.status_code == 200:
        f = open("obsidian_canvas_generator.py", "w")
        f.write(response.text)
        f.close()
        return True
    else:
        return False
    
def download_build_script():
    response = requests.get("https://raw.githubusercontent.com/Scavix/links-to-obsidian-canvas/main/auto_updater_build_script.bat")
    if response.status_code == 200:
        f = open("auto_updater_build_script.bat", "w")
        f.write(response.text)
        f.close()
        return True
    else:
        return False
    
def download_both():
    res1=download_source()
    res2=download_build_script()
    if res1 and res2:
        return True
    else:
        if res1:
            os.remove("obsidian_canvas_generator.py")
        if res2:
            os.remove("auto_updater_build_script.bat")
        return False
    

if __name__ == "__main__":
    main()
