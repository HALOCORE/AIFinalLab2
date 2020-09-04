#pragma once
#include<iostream>
#include<fstream>
#include<vector>

class Chess5AI;
using namespace std;

class IOManager{
public:
    IOManager(Chess5AI & m_cai);
    void output_basic(ostream & osm);
    void input_basic(istream & ism, int & x, int & y);
    void output_file();
private:
    Chess5AI* cai;
};