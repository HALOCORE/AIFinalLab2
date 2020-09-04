#include "IOManager.hpp"
#include "Chess5AI.hpp"

IOManager::IOManager(Chess5AI & m_cai){
    cai = &m_cai;
}

void IOManager::input_basic(istream & ism, int &x, int &y){
    ism >> x;
    ism >> y;
    if(x == -4 && y == -4) {
        cout << "\n#END." << endl;
        cerr << "# Chess5AI END.\n";
        exit(0);
    }
    //输入不合法，则重复上次的输入
    if(x >= 15 || x < 0 || y >= 15 || y < 0){
        x = cai->last_x;
        y = cai->last_y;
    } 
}

void IOManager::output_basic(ostream & osm){
    auto str_gr = [](int gr){
        if(gr == GR_AI_WIN) return "AI win.";
        else if(gr == GR_USER_WIN) return "USER win.";
        else if(gr == GR_NOT_DONE) return "NOT DONE.";
        else if(gr == GR_EVEN) return "even.";
        else return "!undefined.";
    };
    auto str_turn = [](bool uturn){return uturn ? "USER" : "AI";};
    auto str_chess = [](int cp){
        if(cp == 0) return '.';
        else if(IS_CP_USER(cp)) return 'X';
        else if(IS_CP_AI(cp)) return 'O';
        else return 'E';
    };
    osm << "\n#STATUS OUTPUTING..." << endl;
    osm << "tick: " << cai->step_tick << endl;
    osm << "status: " << str_gr(cai->game_result) << endl;
    osm << "turn: " << str_turn(cai->user_turn) << endl;
    osm << "last_step: " << str_turn(!cai->user_turn) 
        << " (" << cai->last_x << ", " << cai->last_y << ")" << endl;
    for(auto & row : cai->chessmap){
        for(auto & elem : row){
            osm << str_chess(elem) << " ";
        }
        osm << endl;
    }
}

void IOManager::output_file(){
    ofstream file;
    //写入文件，且若已有文件则截断
    file.open("./output.txt", ios::out | ios::trunc);

    file << "AI \t ME" << endl;
    int step = 1;
    for(int step=1; step <= cai->step_tick; step++){
        bool is_cp_found = false;
        for(int i=0; i<15; i++){
            for(int j=0; j<15; j++){
                if(step % 2 == 1 && cai->chessmap[i][j] == TO_CP_AI(step)){
                    file << "[" << i << "," << j << "] \t";
                    is_cp_found = true;
                }
                if(step % 2 == 0 && cai->chessmap[i][j] == TO_CP_USER(step)){
                    file << "[" << i << "," << j << "] \n";
                    is_cp_found = true;
                }
            }
        }
        assert(is_cp_found);
    }
    if(cai->user_turn) file<<"\nAI Win!"<<endl;
    else file << "ME Win!"<<endl;
}



