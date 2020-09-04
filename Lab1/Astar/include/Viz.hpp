#include "include_all.hpp"
using namespace std;

class Viz {
public:
    static void show_puzmap(vector<vector<int>> & puzmap);
    static void show_dirmap(vector<vector<int>> & puzmap, vector<vector<char>> & dirmap);
    static void check_and_showpath(vector<vector<int>> & puzmap, vector<char> & dirs, int start_i, int start_j, int target_i, int target_j, bool show_path);
};