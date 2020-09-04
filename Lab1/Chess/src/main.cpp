#include <iostream>
#include "Chess5AI.hpp"
#include "IOManager.hpp"
using namespace std;

int main(){
    cout << "# chess 5 start ..." << endl;

    Chess5AI c5ai(false);
    IOManager iom(c5ai);
    c5ai.debug_iom = &iom; //debug

    c5ai.step_ai();
    iom.output_basic(cout);

    for(int i=0; i<100; i++){
        
        //USER
        while(true){
            cout << "\n#======================= please input valid x y: ";
            int user_stepx, user_stepy;
            iom.input_basic(cin, user_stepx, user_stepy);
            cout << endl; //输入流的换行不会写入输出流。输出流也需要换行
            bool valid = c5ai.step_userin(user_stepx, user_stepy);
            if(valid) break;
        }
        //用户赢了，结束
        if(c5ai.game_result != GR_NOT_DONE) break;
        
        //AI
        c5ai.step_ai();
        iom.output_basic(cout);

        //AI赢了，结束
        if(c5ai.game_result != GR_NOT_DONE) break;
    }

    iom.output_file();
    cout<<"#END. game done.\n";
    cerr<<"# Chess5AI game finish. True->AI, False->User: " << c5ai.user_turn << "END.\n";

}