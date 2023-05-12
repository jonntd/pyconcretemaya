
        #define SECRET_NUM 0x1D
        #define SECRET_KEY_LEN 16
        static const unsigned char* GetSecretKey()
        {
            unsigned int i = 0;
            static unsigned char key[] = {(0x43 ^ (0x1D - 0)), (0x85 ^ (0x1D - 1)), (0x6B ^ (0x1D - 2)), (0x80 ^ (0x1D - 3)), (0xB9 ^ (0x1D - 4)), (0x60 ^ (0x1D - 5)), (0xBE ^ (0x1D - 6)), (0xC3 ^ (0x1D - 7)), (0x9 ^ (0x1D - 8)), (0x90 ^ (0x1D - 9)), (0x87 ^ (0x1D - 10)), (0xAA ^ (0x1D - 11)), (0xDF ^ (0x1D - 12)), (0xAC ^ (0x1D - 13)), (0x6A ^ (0x1D - 14)), (0xB2 ^ (0x1D - 15)), 0/* terminal char */};
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
    