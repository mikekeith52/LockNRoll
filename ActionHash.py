class ActionHash:
    def __init__(self):
        self.table = []
        for i in range(16):
            self.table.append(f'PlayNextDietoSpace_{i}')
    
    def __len__(self):
        return len(self.table)            
    
    def get(self,i):
        return self.table[i]

if __name__ == '__main__':
    print(ActionHash().table)