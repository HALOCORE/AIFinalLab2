#include "Chess5AI.hpp"
#include "IOManager.hpp"
#include <algorithm>
using namespace std;

Chess5AI::Chess5AI(bool user_first)
    :chessmap(15, vector<int>(15, 0)),
    hotmap(15, vector<int>(15, 0)),
    sim_stack(),
    tree_counter()
{
    step_tick = 0; 
    user_turn = user_first;
    game_result = GR_NOT_DONE;
    last_x = -1;
    last_y = -1;
}

bool Chess5AI::step_ai(){
    score_f(true);
    int x, y;
    calc_ai_game_step(x, y);
    assert(chessmap[x][y] == 0); //这个位置必须可以走
    
    step(x, y);
    last_x = x; last_y = y;
    DBG(" ai@ "<<x<<","<<y);
    game_result = check_game_result();
    return true;
}

bool Chess5AI::step_userin(int x, int y){
    if(chessmap[x][y] != 0) return false;
    score_f(true);
    step(x, y);
    last_x = x; last_y = y;
    DBG(" user@ "<<x<<","<<y);
    game_result = check_game_result();
    return true;
}

void Chess5AI::step(int i, int j){
    assert(chessmap[i][j] == 0);
    step_tick++;

    int cp = step_tick;
    if(user_turn) cp = TO_CP_USER(cp);
    else cp = TO_CP_AI(cp);
    
    chessmap[i][j] = cp;
    user_turn = !user_turn;
}

int Chess5AI::check_game_result(){
    int score = score_f();
    
    if(score == SC_AI_5) return GR_AI_WIN;
    if(score == SC_USER_5) return GR_USER_WIN;
    return GR_NOT_DONE;
    //TODO: 还没处理平局
}

void Chess5AI::sim_push(int i, int j){
    assert(chessmap[i][j] == 0);
    step(i, j);
    sim_stack.push_back(pair<int,int>(i,j));
}

void Chess5AI::sim_pop(){
    int i = sim_stack.back().first;
    int j = sim_stack.back().second;
    //检查pop的step是否合理
    assert((IS_CP_AI(chessmap[i][j]) && user_turn)
        ||(IS_CP_USER(chessmap[i][j]) && !user_turn));
    
    chessmap[i][j] = 0;
    step_tick--;
    user_turn = !user_turn;
    sim_stack.pop_back();
}


int Chess5AI::score_f(bool dbg){
    const int c5_init = -2;
    
    //整个检查期间
    int ai_2 = 0, user_2 = 0;
    int ai_3 = 0, user_3 = 0;
    int ai_4 = 0, user_4 = 0;
    int ai_5 = 0, user_5 = 0;
    
    //检查一行期间
    int ai_count, user_count, space_count, circle5[5];
    int check_index;

    //调试，检查一组是否255。
    int dbg_cum = 0;

    //用于更新计数状态的lambda
    auto lam_check = [&] (int cp){
        dbg_cum++;
        if(IS_CP_USER(cp)) user_count++;
        else if(IS_CP_AI(cp)) ai_count++;
        else if(cp == 0) space_count++;
        else assert(false);

        assert(check_index < 5); //检查数组越界
        int cp_rep = circle5[check_index];
        if(cp_rep != c5_init){
            if(IS_CP_AI(cp_rep)) ai_count--;
            if(IS_CP_USER(cp_rep)) user_count--;
            if(cp_rep == 0) space_count--;
            assert(ai_count + user_count + space_count == 5); //各种棋子之和应该等于5
        }
        
        circle5[check_index] = cp;
        check_index = (check_index + 1) % 5;
        
        if(ai_count == 2 && user_count == 0) ai_2++;
        if(user_count == 2 && ai_count == 0) user_2++;
        if(ai_count == 3 && user_count == 0) ai_3++;
        if(user_count == 3 && ai_count == 0) user_3++;
        if(ai_count == 4 && user_count == 0) ai_4++;
        if(user_count == 4 && ai_count == 0) user_4++;
        if(ai_count == 5) {ai_5++;}
        if(user_count == 5) {user_5++;}
    };

    //用于检查 (i,j) 合法的lambda
    auto lam_valid = [](int i, int j){
        return i >= 0 && i < 15 && j >= 0 && j < 15;
    };

    //用于初始化变量
    auto lam_clear_flags = [&](){
        ai_count = 0;
        user_count = 0;
        space_count = 0;
        for(int i=0; i<5; i++) circle5[i] = c5_init;
        check_index = 0;
    };

    dbg_cum = 0;
    //检查横向
    for(int i=0; i<15; i++){
        lam_clear_flags();
        for(int j=0; j<15; j++){
            lam_check(chessmap[i][j]);
        }
    }
    assert(dbg_cum == 225);

    dbg_cum = 0;
    //检查竖向
    for(int j=0; j<15; j++){
        lam_clear_flags();
        for(int i=0; i<15; i++){
            lam_check(chessmap[i][j]);
        }
    }
    assert(dbg_cum == 225);

    dbg_cum = 0;
    //检查左上-右下对角线
    for(int tj = 14, ti = -14; 
        tj > -15 && ti < 15; 
        tj--, ti++)
    {
        lam_clear_flags();
        int i = max(ti, 0);
        int j = max(tj, 0);
        assert(lam_valid(i, j)); //如果i,j非法，逻辑错误
        //DBG("对角线检查 "<< DSC(i) << DSC(j));
        for(int k=0; k<15; k++){
            if(!lam_valid(i+k, j+k)) break;
            lam_check(chessmap[i+k][j+k]);
        }
    }
    assert(dbg_cum == 225);

    dbg_cum = 0;
    //检查左下-右上对角线
    for(int tj = -14, ti = 0; 
        tj < 15 && ti < 29; 
        tj++, ti++)
    {
        lam_clear_flags();
        int i = min(ti, 14);
        int j = max(tj, 0);
        assert(lam_valid(i, j)); //如果i,j非法，逻辑错误
        for(int k=0; k<15; k++){
            if(!lam_valid(i-k, j+k)) break;
            lam_check(chessmap[i-k][j+k]);
        }
    }
    assert(dbg_cum == 225);

    //这种情况不应当出现：ai和user同时赢
    assert(!(ai_5>0 && user_5>0));
    if(ai_5 > 0) return SC_AI_5;
    if(user_5 > 0) return SC_USER_5;
    
    if(dbg){
        fprintf(stderr, "# debug score_f {ai,user}: 4{%d,%d} 3{%d,%d} 2{%d,%d}\n",
                ai_4, user_4, ai_3, user_3, ai_2, user_2);
    }

    return (ai_4 - user_4)*8000 
    + (ai_3 - user_3)*400 
    + (ai_2 - user_2)*10;
}

void Chess5AI::game_tree_span(GTNode* node, int depth){
    tree_counter[depth]++;
    if(depth == 0) return;
    //DBG(DSC(depth));
    if(node->score == SC_AI_5){
        assert(!node->is_max); return; //该USER了
    }
    if(node->score == SC_USER_5){
        assert(node->is_max); return; //该AI了
    }
    
    //获得选择 score, x, y
    vector<pair<int, int>> chs;
    get_choices(chs);
    
    //评估函数预估
    vector<pair<int, pair<int,int>>> estimated_chs;
    // debug_iom->output_basic(cerr);
    for(auto & ch : chs){
        //下棋，计算函数值
        int i = ch.first, j = ch.second;
        
        sim_push(i, j); //棋盘状态修改
        int sc = score_f();
        sim_pop(); //棋盘状态恢复

        estimated_chs.push_back(pair<int, pair<int,int>>(sc, ch));
    }
    if(node->is_max){
        //先最大的
        std::sort(estimated_chs.begin(), estimated_chs.end(), std::greater<>());
        assert(estimated_chs.front().first >= estimated_chs.back().first);
    }
    else{
        //先最小的
        std::sort(estimated_chs.begin(), estimated_chs.end());
        assert(estimated_chs.front().first <= estimated_chs.back().first);
    }
    
    // 调试
    // for(auto & cps : estimated_chs){
    //     int sc = cps.first;
    //     int i = cps.second.first;
    //     int j = cps.second.second;
    //     cerr << "评估:" << "ismax:" << node->is_max << " sc:" << sc << " i,j:" << i << ","<< j<< endl;
    // }

    //最佳分数。初始值是，最大值点=SC_USER_5 ...
    int best_score = node->is_max ? SC_USER_5 : SC_AI_5; 
    //更新分数的lambda
    auto update_best_score = [&](int tscore){
        if(node->is_max && tscore >= best_score)
            best_score = tscore;
        else if(!(node->is_max) && tscore <= best_score)
            best_score = tscore;
    };

    for(auto & cps : estimated_chs){
        int sc = cps.first;
        int i = cps.second.first;
        int j = cps.second.second;
        
        sim_push(i, j); //棋盘状态修改
        assert(sc == score_f()); //如果出错，说明此前计算的分数和现在不一致
        GTNode* snode = new GTNode(i, j, sc, !node->is_max);
        snode->ab_filter = best_score; snode->ab_enabled = AB_ENABLE;  //启用a,b剪枝
        node->childs.push_back(snode); //给节点添加孩子
        game_tree_span(snode, depth-1);
        update_best_score(snode->score);
        sim_pop();  //棋盘状态恢复

        //a-b 剪枝判断
        if(node->ab_enabled){
            if(node->is_max && best_score >= node->ab_filter) break;
            if(!node->is_max && best_score <= node->ab_filter) break;
        }
    }

    //改写最佳分数
    node->score = best_score;
}

void Chess5AI::calc_ai_game_step(int &i, int &j){
    assert(user_turn == false);
    tree_counter.clear();
    for(int i=0; i<=TREE_DEPTH; i++) {
        tree_counter.push_back(0); //一共TREE_DEPTH+1个0
    }    

    //根节点：无所谓 i,j,sc的数值。是个max节点。
    GTNode* game_tree = new GTNode(-1, -1, 0, true);
    game_tree_span(game_tree, TREE_DEPTH); //展开最大层数为TREE_DEPTH
    assert(game_tree->childs.size() > 0);

    bool check = false;
    for(GTNode* node : game_tree->childs){
        if(node->score == game_tree->score){
            i = node->x;
            j = node->y;
            check = true; break;
        }
    }

    //调试代码
    cerr << "# Game-Tree Count: ";
    for(auto & c : tree_counter){
        cerr << c <<"|";
    }
    cerr << endl;
    DBG(DSC(game_tree->score));

    assert(check);
    delete game_tree;
}

void Chess5AI::get_choices(vector<pair<int, int>> & chs){
    //清零热度图
    for(int i=0; i<15; i++)
        for(int j=0; j<15; j++)
            hotmap[i][j] = 0;
    
    auto hot_span = [&](int ci, int cj){
        int hot_radius = 2;
        int i = max(0, ci - hot_radius);
        for(; i<=min(14, ci + hot_radius); i++){
            int j = max(0, cj - hot_radius);
            for(; j<=min(14, cj + hot_radius); j++){
                hotmap[i][j] = 1;
            }
        }
    };

    //热度扩张
    for(int i=0; i<15; i++){
        for(int j=0; j<15; j++){
            int cp = chessmap[i][j];
            if(cp != 0){
                hot_span(i, j);
            }
        }
    }
    hot_span(7, 7);

    //选出choices
    chs.clear();
    for(int i=0; i<15; i++){
        for(int j=0; j<15; j++){
            int cp = chessmap[i][j];
            if(cp == 0 && hotmap[i][j] > 0){
                chs.push_back(pair<int,int>(i, j));
            }
        }
    }
}