import torch.utils.data
import torch.nn.utils
import numpy as np
from torch.utils.data import Dataset

class CFGKT_dataset(Dataset):
    def __init__(self, group, n_ques, n_concept,max_seq):
        self.samples = group
        self.n_ques = n_ques
        self.max_seq = max_seq
        self.data = []
        self.n_concept = n_concept

        for que, conc, ans, timestamp, spendtime in self.samples:
            if len(que) >= self.max_seq:
                self.data.extend([(que[l:l + self.max_seq], ans[l:l + self.max_seq],
                                   conc[l:l + self.max_seq],timestamp[l:l + self.max_seq],
                                   spendtime[l:l + self.max_seq]) for l in range(len(que)) if l % self.max_seq == 0])
            elif len(que) <= self.max_seq and len(que) > 50:
                self.data.append((que, ans, conc,timestamp,spendtime))
            else:
                continue

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        q, a, c, timestamp, spendtime = self.data[idx]
        q = np.array(list(map(int, q)))
        a = np.array(list(map(int, a)))
        c = np.array(list(map(int, c)))
        timestamp = np.array(list(map(int, timestamp)))
        spendtime = np.array(list(map(int, spendtime)))

        skill = np.ones(self.max_seq) * self.n_ques
        skill[:len(q)] = q

        concept = np.ones(self.max_seq) * self.n_concept
        concept[:len(q)] = c

        spent = np.ones(self.max_seq) * 301
        spent[:len(spendtime)] = spendtime
        spent[len(q) - 1] = 301

        time_stamp = np.ones(self.max_seq) * 1441
        time_stamp[:len(timestamp)] = timestamp
        time_stamp[len(q) - 1] = 1441

        time_stamp_tensor = torch.LongTensor(time_stamp)
        a = time_stamp_tensor[:-1]
        sub = torch.cat((torch.LongTensor([0]), a), dim=-1)

        sub[len(q) - 1] = 1441
        interval = time_stamp_tensor - sub
        interval[len(q) - 1:] = 1441
        interval = interval.clip(0, 1441)


        mask = np.zeros(self.max_seq)
        mask[1:len(a) - 1] = 0.9
        mask[len(a) - 1] = 1

        labels = np.ones(self.max_seq) * -1
        labels[:len(a)] = a

        qa = np.ones(self.max_seq) * (self.n_concept * 2 + 1)
        qa[:len(c)] = c + a * self.n_concept
        qa[len(c) - 1] = self.n_concept * 2 + 1
        return (torch.LongTensor(qa), torch.LongTensor(skill), torch.LongTensor(labels), torch.FloatTensor(mask),
                torch.LongTensor(concept), torch.LongTensor(spent), interval)
