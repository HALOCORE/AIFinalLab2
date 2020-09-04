#include "IDAstar.hpp"

#define BIG_INT 100000

IDAstar::IDAstar(vector<vector<int>> & m_map)
    :gval_map(m_map.size(), vector<int>(m_map[0].size(), BIG_INT)),
    pmap(), dir_stack(), dfs_count()
{
    this->pmap = m_map; //is this a copy or ref? 应该是复制
    this->pmap_i_max = m_map.size() - 1;
    this->pmap_j_max = m_map[0].size() - 1;
    DBG(" i_max:"<<pmap_i_max<<" j_max:"<<pmap_j_max);
}


void IDAstar::find_path(int start_i, int start_j, int end_i, int end_j, vector<char>& path_dir){
    //初始化
    for(auto & r : gval_map)
        for(auto & e : r) e = BIG_INT;
    gval_map[start_i][start_j] = 0;

    tmp_target_i = end_i;
    tmp_target_j = end_j;
    //如果起点和终点相同，未处理
    assert(!(start_i == end_i && start_j == end_j));
    dir_stack.clear();
    int limit_f = heuristic_f(start_i, start_j, end_i, end_j);
    while(true){
        DBG("---- path_dfs: " << limit_f << " ----");
        //每轮初始化
        for(auto & r : pmap)
            for(auto & e : r) if(e == -1) e = 0;
        dfs_depth_count.clear();
        dfs_depth_count.assign((size_t)limit_f + 1, 0);
        dfs_count = 0;
        bool path_find = path_dfs(start_i, start_j, 0, limit_f);
        if(!path_find) limit_f+=2;
        else break;
    }
    cout << "dfs各层次访问次数: ";
    for(auto & x : dfs_depth_count){
        cout << x << " | ";
    }
    cout << endl << "dfs总访问次数: " << dfs_count << endl;

    //保存结果
    path_dir = dir_stack; //是复制吗？
}


int IDAstar::heuristic_f(int current_i, int current_j, int target_i, int target_j){
    return (target_i - current_i) + (target_j - current_j);
}


bool IDAstar::path_dfs(int cur_i, int cur_j, int gval, int limit_f){
    dfs_depth_count[gval]++;
    dfs_count++;
    
    //不可达/重复
    if(pmap[cur_i][cur_j] != 0) {
        return false;
    }

    //目标到达
    if(cur_i == tmp_target_i && cur_j == tmp_target_j){
        assert(pmap[cur_i][cur_j] == 0);
        return true;
    }

    //次优解到达
    if(gval > gval_map[cur_i][cur_j]){
        return false;
    }

    //gval <= gval_map中的值
    gval_map[cur_i][cur_j] = gval;

    
    //标记
    pmap[cur_i][cur_j] = -1;

    int i4[] = {-1, +1, 0, 0};
    int j4[] = {0, 0, -1, +1};
    char d4[] = {'U', 'D', 'L', 'R'};
    int i,j;
    //第一步：找到最佳方向。DFS只要找到可行方向
    //TODO: 不判重效率不行
    vector<pair<int, int>> directions;
    for(int k=0; k<4; k++){
        i = min(pmap_i_max, max(0, cur_i+i4[k])); 
        j = min(pmap_j_max, max(0, cur_j+j4[k])); 
        if( i == cur_i && j == cur_j) continue;
        int this_h = heuristic_f(i, j, tmp_target_i, tmp_target_j);
        int this_f = this_h + gval + 1;
        if(this_f <= limit_f){
            directions.push_back(pair<int,int>(this_f, k));
        }
    }

    std::sort(directions.begin(), directions.end());
    assert(directions[0] <= directions[1]); //排序假设

    for(auto & p : directions){
        int f = p.first;
        int k = p.second;
        int i = cur_i + i4[k];
        int j = cur_j + j4[k];
        // DBG("push_back f=" << f << " @ " << i << ", " << j);
        this->dir_stack.push_back(d4[k]);//方向入栈
        bool found = this->path_dfs(i, j, gval + 1, limit_f);
        if(found) {
            //pmap[cur_i][cur_j] = 0;
            return true; //成功。不断返回
        }else{
            // DBG("pop_back");
            this->dir_stack.pop_back();//方向出栈
        }
    }
    
    //如果到这里，说明没找到
    return false;

}