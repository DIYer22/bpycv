mkdir ycb_demo
cd ycb_demo/

# prepare demo code and data
git clone https://github.com/DIYer22/bpycv
git clone https://github.com/DIYer22/bpycv_example_data

cd bpycv/example/

blender -b -P ycb_demo.py
