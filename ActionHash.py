class ActionHash:
    def __init__(self):
        self.table = []
        for c in 'RBGY':
            for n in '1234':
                for s in range(16):
                    self.table.append((c+n,s))
        for s in range(16):
            self.table.append(('JO',s))
    
    def __len__(self):
        return len(self.table)            
    
    def get(self,i):
        return self.table[i]