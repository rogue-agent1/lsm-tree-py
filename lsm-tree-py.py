#!/usr/bin/env python3
"""Log-Structured Merge Tree (LSM-Tree) — in-memory simulation."""
import sys
from bisect import insort

class LSMTree:
    def __init__(self,memtable_size=4):
        self.memtable={};self.memtable_size=memtable_size
        self.levels=[]  # list of sorted runs (list of (key,value) sorted by key)
    def put(self,key,value):
        self.memtable[key]=value
        if len(self.memtable)>=self.memtable_size:self._flush()
    def _flush(self):
        run=sorted(self.memtable.items())
        self.levels.append(run);self.memtable={}
        if len(self.levels)>3:self._compact()
    def _compact(self):
        merged={};
        for run in self.levels:
            for k,v in run:merged[k]=v
        self.levels=[sorted(merged.items())]
    def get(self,key):
        if key in self.memtable:
            v=self.memtable[key];return None if v is None else v
        for run in reversed(self.levels):
            lo,hi=0,len(run)-1
            while lo<=hi:
                mid=(lo+hi)//2
                if run[mid][0]==key:
                    v=run[mid][1];return None if v is None else v
                elif run[mid][0]<key:lo=mid+1
                else:hi=mid-1
        return None
    def delete(self,key):self.put(key,None)  # tombstone
    def scan(self,lo,hi):
        result={}
        for run in self.levels:
            for k,v in run:
                if lo<=k<=hi:result[k]=v
        for k,v in self.memtable.items():
            if lo<=k<=hi:result[k]=v
        return{k:v for k,v in sorted(result.items()) if v is not None}

def main():
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        t=LSMTree(memtable_size=3)
        t.put("a","1");t.put("b","2");t.put("c","3")  # triggers flush
        assert t.get("a")=="1"
        assert t.get("b")=="2"
        t.put("d","4");t.put("a","5")  # update a
        assert t.get("a")=="5"
        t.delete("b")
        assert t.get("b") is None
        r=t.scan("a","d")
        assert "b" not in r
        assert r.get("a")=="5"
        # Compaction
        for i in range(20):t.put(f"k{i:02d}",str(i))
        assert t.get("k05")=="5"
        assert len(t.levels)<=4  # compacted
        print("All tests passed!")
    else:
        t=LSMTree()
        for i in range(10):t.put(f"key{i}",f"val{i}")
        print(f"key5 = {t.get('key5')}")
        print(f"Levels: {len(t.levels)}, Memtable: {len(t.memtable)}")
if __name__=="__main__":main()
