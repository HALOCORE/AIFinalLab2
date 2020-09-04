#pragma once
#include <assert.h>
#define DBGE(X) if(true){cerr <<__FUNCTION__<<" debug call. "<<endl;X}
#define DBG(X) if(true){cerr <<__FUNCTION__<<": "<<X<<endl;}
#define DSC(X) " "#X"=" << (X) << ", "