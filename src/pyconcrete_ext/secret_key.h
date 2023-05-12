
        #define SECRET_NUM 0x15
        #define SECRET_KEY_LEN 16
        static const unsigned char* GetSecretKey()
        {
            unsigned int i = 0;
            static unsigned char key[] = {(0x89 ^ (0x15 - 0)), (0xF8 ^ (0x15 - 1)), (0xBF ^ (0x15 - 2)), (0x86 ^ (0x15 - 3)), (0x5D ^ (0x15 - 4)), (0xAB ^ (0x15 - 5)), (0xFD ^ (0x15 - 6)), (0xD ^ (0x15 - 7)), (0x13 ^ (0x15 - 8)), (0x52 ^ (0x15 - 9)), (0x36 ^ (0x15 - 10)), (0x18 ^ (0x15 - 11)), (0xF7 ^ (0x15 - 12)), (0xEE ^ (0x15 - 13)), (0xCD ^ (0x15 - 14)), (0x1F ^ (0x15 - 15)), 0/* terminal char */};
            static int is_encrypt = 1/*true*/;
            if( is_encrypt )
            {
                for(i = 0 ; i < SECRET_KEY_LEN ; ++i)
                {
                    key[i] = key[i] ^ (SECRET_NUM - i);
                }
                is_encrypt = 0/*false*/;
            }
            return key;
        }
    