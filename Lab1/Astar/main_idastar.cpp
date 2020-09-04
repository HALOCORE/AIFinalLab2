#include <iostream>
#include <FileIO.hpp>
#include "Astar.hpp"
#include "IDAstar.hpp"
#include "Viz.hpp"
#include <time.h>

using namespace std;

int main(int argc, char** argv){
    cout << "\n # IDA* start ..."<<endl;
    if(argc != 6){
        cout << "请依次输入：文件名 起点i 起点j 终点i 终点j" << endl << "程序结束。" << endl;
    }
    
    const char* filename = argv[1];
    vector<vector<int>> puzmap;
    FileIO::read_map_from_file(filename, puzmap);
    // Viz::show_puzmap(puzmap);

    //set and run
    int start_i, start_j, target_i, target_j;
    start_i = atoi(argv[2]);
    start_j = atoi(argv[3]);
    target_i = atoi(argv[4]);
    target_j = atoi(argv[5]);

    IDAstar m_idastar(puzmap);
    vector<char> path_dir;
    
    timespec t1, t2;
    clock_gettime(CLOCK_REALTIME, &t1);
    m_idastar.find_path(start_i, start_j, target_i, target_j, path_dir);
    clock_gettime(CLOCK_REALTIME, &t2);
    double time_pass = (t2.tv_sec - t1.tv_sec) + (t2.tv_nsec - t1.tv_nsec)/1e9;
    

    //屏幕显示
    Viz::check_and_showpath(puzmap, path_dir, start_i, start_j, target_i, target_j, true);
    for(auto c : path_dir){
        cout << c;
    }
    cout<<endl<<path_dir.size()<<endl;

    //文件输出
    FileIO::write_path_to_file("./output_IDA.txt", path_dir, time_pass);

    cout << "\n # IDA* end."<<endl;
}


