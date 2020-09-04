#pragma once
#include <my_debug.hpp>
#include <iostream>
#include <vector>
#define IS_CP_USER(x) (x > 0)
#define IS_CP_AI(x) (x < 0)
#define TO_CP_USER(x) (x)
#define TO_CP_AI(x) (-x)

#define GR_USER_WIN -1
#define GR_AI_WIN 1
#define GR_NOT_DONE 0
#define GR_EVEN 233


#define TREE_DEPTH 3

#define SC_AI_5 9999999
#define SC_USER_5 -9999999

#define AB_DISABLE 0
#define AB_ENABLE 1
// #define AB_GREATER_EQUAL 1
// #define AB_LESS_EQUAL -1

using namespace std;

class IOManager; //debug

class GTNode{
public:
    GTNode():childs(){}
    ~GTNode(){
        for(GTNode* p : childs) delete p;
    }
    GTNode(int mx, int my, int mscore, bool mis_max):childs(){
        x = mx; y = my; score = mscore; is_max = mis_max;
        ab_filter = 0; ab_enabled = AB_DISABLE;
    }
    int x, y, score;
    int ab_filter;
    int ab_enabled;
    bool is_max;
    vector<GTNode*> childs;
};

class Chess5AI{
public:
    Chess5AI(bool user_first);
    bool step_ai();
    bool step_userin(int x, int y);

public:
    int step_tick;
    bool user_turn;
    int game_result;
    int last_x, last_y;
    vector<vector<int>> chessmap;

    IOManager* debug_iom; //debug

private:
    void step(int i, int j);
    //检查结果状态
    int check_game_result();
    
    //计算博弈树
    vector<pair<int,int>> sim_stack;
    /*统计*/vector<int> tree_counter;
    void sim_push(int i, int j);
    void sim_pop();
    int score_f(bool dbg = false); //AI要让score最大化，USER要最小化
    void game_tree_span(GTNode* node, int depth);
    void calc_ai_game_step(int& i, int& j); //调用此函数
    
    
    //热度图选择
    vector<vector<int>> hotmap;
    void get_choices(vector<pair<int, int>> & chs);
};