<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=default"></script>

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
+ CMake Sample
  - make visual studio project
  - has a static lib and a MFC application




Here is an example MathJax inline rendering \\( 1/x^{2} \\), and here is a block rendering: 
\\[ \frac{1}{n^{2}} \\]

$$x_{1,2} = \frac{-b \pm \sqrt{b^2-4ac}}{2b}.$$
