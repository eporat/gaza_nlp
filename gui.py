
import PySimpleGUI as sg
import os.path
import json
# First the window layout in 2 columns

file_list_column = [
    [
        sg.Text("Browse Files", font=("Arial", 18)),
        sg.In(size=(40, 10), enable_events=True, key="-FOLDER-", font=("Arial", 18)),
        sg.FolderBrowse(font=("Arial", 18, 'bold')),
    ],
]

labeling_column = [
    [
        sg.Text("File name: ", font=("Arial", 18)),
        sg.Text("Unknown file", key="-FILENAME-", font=("Arial", 18), background_color='white', text_color='black', justification='center')
    ],

    [
        sg.Text("Area: ", font=("Arial", 18)),
        sg.Text("Unknown area", key="-AREA-", font=("Arial", 18), background_color='white', text_color='black', justification='center')
    ],


    [
        sg.Text("Start Date: ", font=("Arial", 18)),
        sg.Input('DD:MM:YY HH:MM:SS', font=("Arial", 18), key='STARTDATE'), sg.CalendarButton('Calendar', target='STARTDATE', no_titlebar=False, font=('Arial', 18, 'bold'), close_when_date_chosen=True)
    ],

    
    [
        sg.Text("END Date: ", font=("Arial", 18)),
        sg.Input('DD:MM:YY HH:MM:SS', font=("Arial", 18), key='ENDDATE'), sg.CalendarButton('Calendar', target='ENDATE', no_titlebar=False, font=('Arial', 18, 'bold'), close_when_date_chosen=True)
    ],

    [
        sg.Text("Text: ", font=("Arial", 18)),
        sg.Multiline("", key="-TEXT-", font=("Arial", 18), size=(60, 15), background_color='white', text_color='black', justification='left', expand_y=True)
    ]
]

submit_column = [
    [sg.OK('OK', font=("Arial", 18), pad=50, key='OK'), sg.OK('Skip', font=("Arial", 18), pad=50, key='SKIP', button_color='red'), 
    sg.OK('Back', font=("Arial", 18), pad=50, key='BACK', button_color='blue')]
]

column_names = ["airstrike IDF", "rocket PAL",
"mortar PAL",
"shelling IDF",
"incursion IDF",
"firing IDF",
"Israel Killed",
"Israel Injured",
"Civ Killed IDF",
"Civ Injured IDF",
"Hamas Killed IDF",
"Hamas Injured IDF",
"Other Miliranr Killed IDF",
"Other Militant Injured IDF",
"High Ranking Hamas Killed",
"High Ranking Hamas Injured",
"High Ranking Other Killed",
"High Ranking Other Injured",
"Location Hit/Targeted PAL"]

data_entry_column = [[] for i in range(8)]
for i, column_name in enumerate(column_names):
    data_entry_column[i//3].append(sg.Text(column_name, font=("Arial", 18))) 
    data_entry_column[i//3].append(sg.Spin(values=list(range(100)), key=column_name, font=("Arial", 18),initial_value=0, size=(3,3)))



# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
    ],
    [
        sg.Column(labeling_column)
    ],
    [
        sg.Column(data_entry_column)
    ],
    [
        sg.Column(submit_column, vertical_alignment='center', justification='center')
    ]
]

window = sg.Window("Data Labeling", layout, resizable=True)

fnames = []
file_index = 0
file_entry = None
area_index = 0
areas = []
sentence_index = 0
marked = False

data = json.load(open('data.json', mode='r', encoding='utf-8'))
if not os.path.exists('output.csv'):
    csvfile = open('output.csv', mode='w+')
else:
    csvfile = open('output.csv', mode='a')

def update(file):
    global file_entry, areas, area_index, sentence_index
    window['-FILENAME-'].update(file)
    
    area_index = 0
    sentence_index = 0

    for entry in data:
        if file in entry['file']:
            file_entry = entry
            break
    
    areas = list(file_entry.keys())[1:]
    update_sentence()

def back():
    global sentence_index, area_index, file_index, marked
    if area_index == 0 and sentence_index == 0 and file_index == 0:
        sg.Popup("can't go back!", keep_on_top=True)
        return
    elif area_index == 0 and sentence_index == 0:
        sg.Popup("moving back a file!", keep_on_top=True)
        file_index -= 1
        update(fnames[file_index])
        area_index = 3
        area = areas[area_index]
        sentence_index = len(file_entry[area]['events']) - 1
    elif sentence_index == 0:
        area = areas[area_index]
        area_index -= 1
        sentence_index = len(file_entry[area]['events']) - 1
    else:
        sentence_index -= 1
    update_sentence()

def skip():
    global sentence_index, area_index, file_index, marked
    sentence_index += 1

    area = areas[area_index]
    if sentence_index == len(file_entry[area]['events']):
        area_index += 1
        sentence_index = 0
    
    if area_index == 4:
        file_index += 1
        area_index = 0
        if file_index == len(fnames):
            sg.Popup('No more files!', keep_on_top=True)
        else:
            update(fnames[file_index])
    
    update_sentence()

def update_sentence():
    global sentence_index, area_index, file_index, marked

    area = areas[area_index]
    window["-AREA-"].update(area.capitalize())   
    window['STARTDATE'].update(file_entry[area]["events"][sentence_index]["time"])
    window['ENDDATE'].update(file_entry[area]["events"][sentence_index]["time"])
    # if sentence_index + 1 < len(file_entry[area]["events"]):
    #     window['ENDDATE'].update(file_entry[area]["events"][sentence_index+1]["time"])
    # else:
    #     window['ENDDATE'].update(file_entry[area]["events"][sentence_index]["time"])

    before_sentence = ''.join(map(lambda x: x['content'].strip() + '.', file_entry[area]["events"][:sentence_index]))
    after_sentence = ''.join(map(lambda x: x['content'].strip() + '.', file_entry[area]["events"][sentence_index+1:]))

    window['-TEXT-'].update('')
    window['-TEXT-'].print(before_sentence)
    color = 'red' if file_entry[area]["events"][sentence_index]['marked'] else 'green'
    marked = file_entry[area]["events"][sentence_index]['marked']
    window['-TEXT-'].print(file_entry[area]["events"][sentence_index]["content"].strip() + '.', font=("Arial", 18, 'bold'), text_color=color)
    window['-TEXT-'].print(after_sentence)

    for column_name in column_names:
        window[column_name].update("0")


# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = sorted([
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith(".doc") or f.lower().endswith(".pdf") or f.lower().endswith(".docx")
        ])

        file_index = 0
        if not fnames:
            sg.Popup('Invalid directory', keep_on_top=True)
        else:
            update(fnames[file_index])
    if not fnames:
        continue
    if event == 'OK':
        try:
            row = [str(int(marked)), window['-FILENAME-'].get(), window['-AREA-'].get(), str(sentence_index), window['STARTDATE'].get(), window['ENDDATE'].get()] \
                + [window[datacolumn].get() for datacolumn in column_names]
            csvfile.write(','.join(map(str, row)) + '\n')
            csvfile.close()
            csvfile = open('output.csv', mode='a')
            skip()
        except Exception as e:
            raise e
    if event == 'SKIP':
        skip()
    if event == 'BACK':
        back()

window.close()