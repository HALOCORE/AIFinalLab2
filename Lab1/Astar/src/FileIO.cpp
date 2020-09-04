#include "FileIO.hpp"


using namespace std;

void FileIO::read_map_from_file(const char* filename, vector<vector<int>> & puzmap)
{
    ifstream ifs;
    ifs.open(filename, ios::in);
    if(!ifs.is_open()){
        throw std::invalid_argument("cannot open the file.");
    }
    
    ostringstream tmp;
    tmp << ifs.rdbuf();
    string file_data = tmp.str();
    ifs.close();

    puzmap.clear();
    vector<int> row;
    row.clear();
    for(char c : file_data){
        if(c == '1' || c == '0'){
            row.push_back((int)(c - '0'));
        }
        if((c == '\n' || c == '\r') && row.size() > 0){
            //printf("\\n or \\r encountered.\n");
            puzmap.push_back(row);
            row.clear();
        }
    }
    if(row.size() > 0){
        puzmap.push_back(row);
    }

    size_t rowlen = puzmap[0].size();
    for(auto row : puzmap){
        assert(row.size() == rowlen);
    }
}


void FileIO::write_path_to_file(const char* filename, vector<char> & path, double time){
    ofstream ofs;
    ofs.open(filename, ios::out);

    if(!ofs.is_open()){
        throw std::invalid_argument("cannot open file for write.");
    }

    ofs << time << endl;
    for(char c : path){
        ofs << c;
    }
    ofs << endl << path.size();
}