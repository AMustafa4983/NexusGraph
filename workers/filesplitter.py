class FileSplitter:
    def __init__(self):
        self.sections = {}
        self.section_names = ['TITLE','ABSTRACT','INTRODUCTION','METHODS','RESULTS','DISCUSSION' 
                              ,'Abstract', 'Background', 'Introduction', 'Literature Review', 'Methods',
                              'Results', 'Discussion', 'Conclusion', 'Keywords']

    def split_file_by_section(self, filetext):
        text = filetext['row']['text']
        
        for section_name in self.section_names:
            index = text.find(section_name)
            if index != -1:
                start = index + len(section_name)
                end = text.find(self.section_names[self.section_names.index(section_name) + 1]) if self.section_names.index(section_name) + 1 < len(self.section_names) else len(text)
                self.sections[section_name.lower()] = text[start:end].strip()
            else:
                print("There is no", section_name)
        
        return self.sections