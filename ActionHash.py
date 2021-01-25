class ActionHash:
    def __init__(self):
        self.table = []
        for c in 'RBGY':
            for n in '1234':
                for s in range(16):
                    self.table.append((c+n,s))
        for s in range(16):
            self.table.append(('JO',s))
        self.table.append(('LO','RO'))
    
    def __len__(self):
        return len(self.table)            
    
    def get(self,i):
        return self.table[i]

if __name__ == '__main__':
    print(ActionHash().table)