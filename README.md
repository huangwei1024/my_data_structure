my_lib
======

my lib repository  
save some algorithm and data structure used in work !

---

+ TinyMap
  - use the vector container to implement the map
  - apply to replace the map of small amount data, or the structure of updated low frequency
  - advantages: small memory, quick traversal/insert
  - weakness: insert/delete will lead to rearrangement
+ MultiIndexMMap
  - support multi-set
  - support equal_range search
  - multiple index has memory overhead, but less than the map
  - the actual data stored in a sequential container
  + TODO:
    - storage remove duplicates
+ CompressMap
+ STLAllocator
  - replace std::allocator for memory statistics
