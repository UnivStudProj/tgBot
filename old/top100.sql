PGDMP          )            
    y            top100_tracks    14.0    14.0     �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16457    top100_tracks    DATABASE     q   CREATE DATABASE top100_tracks WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'English_United States.1252';
    DROP DATABASE top100_tracks;
                postgres    false            �            1259    16459    tracks    TABLE     �   CREATE TABLE public.tracks (
    track_pos_number integer NOT NULL,
    track_artist text NOT NULL,
    track_name text NOT NULL
);
    DROP TABLE public.tracks;
       public         heap    postgres    false            �            1259    16458    tracks_track_pos_number_seq    SEQUENCE     �   CREATE SEQUENCE public.tracks_track_pos_number_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.tracks_track_pos_number_seq;
       public          postgres    false    210            �           0    0    tracks_track_pos_number_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.tracks_track_pos_number_seq OWNED BY public.tracks.track_pos_number;
          public          postgres    false    209            \           2604    16462    tracks track_pos_number    DEFAULT     �   ALTER TABLE ONLY public.tracks ALTER COLUMN track_pos_number SET DEFAULT nextval('public.tracks_track_pos_number_seq'::regclass);
 F   ALTER TABLE public.tracks ALTER COLUMN track_pos_number DROP DEFAULT;
       public          postgres    false    210    209    210            �          0    16459    tracks 
   TABLE DATA           L   COPY public.tracks (track_pos_number, track_artist, track_name) FROM stdin;
    public          postgres    false    210   +       �           0    0    tracks_track_pos_number_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.tracks_track_pos_number_seq', 1, false);
          public          postgres    false    209            ^           2606    16464    tracks tracks_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_pkey PRIMARY KEY (track_pos_number);
 <   ALTER TABLE ONLY public.tracks DROP CONSTRAINT tracks_pkey;
       public            postgres    false    210            �    	  x��X]w�}��+n^�Ȳ���,SRbh�k�]}���4�HvO�Y����)!�i�Rdٲ�I��?���d�B� i�=��}���\g���u܎��^�]7t{�c�	~=Ưw��^ָ�.^�{�Z׷�[�IV��w�M;x��G��#k=�KM&��˙K~5\�C�{�_	���7���^1���q�C�zy3�/đq��?�}��o�0�y~�`���ȯ�p �_�W�и�c�S4�s�N��Q~���&���8*YX:��~�Ep�`�=Xܲ^�\�A���Q-�ꁝ���h�zsäm�c����'kI۞��?��v��z��aX���
��؏����Mx�N�W8{H8�M3[����a�}�^��ŅV C�p%���wq_�c�~ V�<<n[x҃�6���Ź3��G����g� P�g.@���fW����
�2u�,S0�\
l��X��{����Uq���E37�%>�h"O/��Yb�)�6�j��L�j�K�����<-y"T�;��&��Bٸ��1 G�ۦ�H��d
�`q��;b���b�D�޸�b ���a�Z�����u�����Jfp��+�>�H2>v��	|@x�>�1�Ұ������B�l�\��M߸�n�	R�9�[ҕ�ѓ�ve/qN�`�Ϳ��v�|�)�u#`@#�S_�l��s'�D��A��>a��7������WY�D�5F�ڒ�S���$N���o-�tꖗ-���vï-�f>����>~���(�n��o.Eq؄�̘�-{�_h�O��=���/�J�~Gՠ�����1��3T�4R�����P�	�>�e�ί��+$Q�����H��\�ݮ��b��UڧA��Cl�S^S�q�P	�-���rVOG9�Tʧ-뉌��'d�;�Q�#��W�-���R*�K�h�d.6nL�����o�a�ARC�|�9���|�-��/��P�I��٦���7q��[J��Ϡc����J�^���� NU��T�>P��H���%�]���m�\��h?mD-�A��#*@>ˊ�f$P2��:�9��3UD�I�sI'�bґ�N�Мaw>կ�K����/N�V����m�5��dc�������'}�����%-�0;�mE�^HA2'�x"� �c��F���TB�i�'V��e�*�zyaCGu@r#�i qy��t�^^o������U���l�Y�S�b_��w/_1�q;"-��܀�W�Qݓ���O�����rU*�+���8\��R�Ң<�D����&�oG�Gi�
�H��*�V��rm	?�F����Є۩�����S�*CD�ɁPE�h'�S0��zK���82�]EuN�ƙ^#
/��'d@*R7#�@�!*�����һ��ca�@Ѷ��Lc�B;'�>[�F�^1���$m��w��ҫ��t7k�@:�E�R�w]�2�j�H`}̜�����Ŭf�8mE[���V=�t��)ڟ����ރ-d�%h~D_��d�=	��Ϟ�/�-T�M�]�gX�0�|��h�@�fޯ-D���2S����vv�+}JǸ�tEQA���hJ�ŴԮS8��R^�p*�̥嚯B�C<l3�	����*@���kl=��B�JYl�z*���bp�3�A͊N�]��3S��`6dϱ��3L����dZ�0����:�Y)>��;�T��|���HE�Z��۳�z
��T?��xZ���k�Wʑ��R�������zS�gò�~�gvMsy���x2r#zї��V]Wx�9�*�q�DhcI&r_�T0����\^�b��bi.-��:�d&�2�{@r�]b:E`~�#��Nx%)w͑LO�(ȕ�{/��x`�����P�ꋁr�m�>92A�'o��A�Kv�/����i���qd��3ڥ;����C{:Tu�{2�kˠ�_J�D���W9svf��A�)g�5�o���,�Tm9�V�V��;������ZXW��ݍ�����r~|��>���đ�H�;Л����%�ȰZC�ǆ�6EY�� qrGi3D��rX��쵨����	8���� ߍ��Ż��=�>Zu��_fb������Q�Dvx�� =���:U!3��ZUO��ܞVS�����lͤa���V�]Z�4�X�[bavj���\Bh#��|re��ګL2T9#�»&�&]~!h4`E���?6�}���UJӁ��l��\T&Ь]�o�I|��/����p3x�A�4�t���kk��n�T�۳z���33rd %�ؒY��H�@�*�Ya������y���a�     