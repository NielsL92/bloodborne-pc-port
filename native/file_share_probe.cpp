// Independent Windows CRT sharing probe; operates only on its new fixture file.
#define NOMINMAX
#include <windows.h>
#include <share.h>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
int wmain(int argc,wchar_t**argv) {
    if(argc!=2)return 2;
    HANDLE create=CreateFileW(argv[1],GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(create==INVALID_HANDLE_VALUE)return 3;
    CloseHandle(create);
    for(int mode: {_SH_DENYWR,_SH_DENYNO}) {
        FILE* first=_wfsopen(argv[1],L"r+b",mode);
        if(!first)return 4;
        errno=0;_set_doserrno(0);
        FILE* second=_wfsopen(argv[1],L"r+b",mode);
        int error=errno;unsigned long dos=0;_get_doserrno(&dos);
        std::printf("{\"share\":\"%s\",\"second_open\":%s,\"errno\":%d,\"doserrno\":%lu}\n",
          mode==_SH_DENYWR?"deny_write":"allow_read_write",second?"true":"false",error,dos);
        if(mode==_SH_DENYWR && (second || error!=EACCES || dos!=ERROR_SHARING_VIOLATION))return 5;
        if(mode==_SH_DENYNO && !second)return 6;
        if(second)std::fclose(second);
        std::fclose(first);
    }
    return 0;
}
