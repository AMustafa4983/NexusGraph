class FileSplitter:
    def __init__(self):
        self.sections = {}
        self.section_names = ['BACKGROUND', 'INTRODUCTION', 'METHODS','Background', 'Introduction', 'Methods']

    def split_file_by_section(self, filetext):
        text = filetext

        self.sections['text'] = text
        for section_name in self.section_names:
            index = text.find(section_name)
            if index != -1:
                start = index + len(section_name)
                self.sections[section_name.lower()] = text[start:].strip()
                print(section_name, "Founded")
            else:
                print("There is no", section_name)
        
        return self.sections