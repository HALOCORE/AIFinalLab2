#include "include_all.hpp"
#include <fstream>
#include <sstream>

using namespace std;

class FileIO{
public:
    static void read_map_from_file(const char* filename, vector<vector<int>> & puzmap);
    static void write_path_to_file(const char* filename, vector<char> & path, double time);
};