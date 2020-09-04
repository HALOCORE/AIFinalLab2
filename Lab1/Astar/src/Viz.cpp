#include "Viz.hpp"

using namespace std;

void Viz::show_puzmap(vector<vector<int>> & puzmap){
    cout<<endl;
    for(auto & row : puzmap){
        for(auto & flag : row){
            char c = ' ';
            if(flag == 1) c = '#';
            if(flag == -1) c = 'X';
            cout<<c<<" ";
        }
        cout<<endl;
    }
}

void Viz::show_dirmap(vector<vector<int>> & puzmap, vector<vector<char>> & dirmap){
    cout<<endl;
    for(int i=0; i<puzmap.size(); i++){
        for(int j=0; j<puzmap[0].size(); j++){
            char c = ' ';
            int pm = puzmap[i][j];
            char dm = dirmap[i][j];
            if(pm == 1) c = '#';
            else if(pm == -1) c = dm;
            else{
                if(dm != 0) c = dm-'A'+'a';
            }
            cout<<c<<' ';
        }
        cout<<endl;
    }
}

void Viz::check_and_showpath(vector<vector<int>> & puzmap, vector<char> & dirs, int start_i, int start_j, int target_i, int target_j, bool show_path)
{
    vector<vector<char>> dirmap(puzmap.size(), vector<char>(puzmap[0].size()));
    int cur_i = start_i, cur_j = start_j;
    for(auto & dir : dirs){
        assert(puzmap[cur_i][cur_j] == 0);
        int i4[] = {-1, +1, 0, 0};
        int j4[] = {0, 0, -1, +1};
        char d4[] = {'U', 'D', 'L', 'R'};
        int i;
        for(i=0; i<4; i++){
            if(dir == d4[i]){
                dirmap[cur_i][cur_j] = dir;
                cur_i = cur_i + i4[i];
                cur_j = cur_j + j4[i];
                break;
            }
        }
        assert(i != 4);
    }
    if(show_path) Viz::show_dirmap(puzmap, dirmap);
    
    if(cur_i != target_i || cur_j != target_j){
        cout << "# !!! check_and_showpath FAILED. !!!" << endl;
    }
    else{
        cout << "# check_and_showpath SUCCEED." << endl;
    }
}