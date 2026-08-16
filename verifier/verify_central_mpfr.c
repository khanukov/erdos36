
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

/* Minimal MPFR ABI declarations; the runtime library is libmpfr.so.6. */
typedef long mpfr_prec_t;
typedef long mpfr_exp_t;
typedef int mpfr_sign_t;
typedef unsigned long mp_limb_t;
typedef struct {
    mpfr_prec_t _mpfr_prec;
    mpfr_sign_t _mpfr_sign;
    mpfr_exp_t _mpfr_exp;
    mp_limb_t *_mpfr_d;
} __mpfr_struct;
typedef __mpfr_struct mpfr_t[1];
typedef __mpfr_struct *mpfr_ptr;
typedef const __mpfr_struct *mpfr_srcptr;
typedef int mpfr_rnd_t;

#define MPFR_RNDN 0
#define MPFR_RNDZ 1
#define MPFR_RNDU 2
#define MPFR_RNDD 3
#ifndef PREC
#define PREC 96
#endif

extern void mpfr_init2(mpfr_ptr, mpfr_prec_t);
extern void mpfr_clear(mpfr_ptr);
extern int mpfr_set_str(mpfr_ptr, const char*, int, mpfr_rnd_t);
extern int mpfr_set(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_set_si(mpfr_ptr, long, mpfr_rnd_t);
extern int mpfr_set_ui(mpfr_ptr, unsigned long, mpfr_rnd_t);
extern int mpfr_add(mpfr_ptr, mpfr_srcptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_sub(mpfr_ptr, mpfr_srcptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_add_ui(mpfr_ptr, mpfr_srcptr, unsigned long, mpfr_rnd_t);
extern int mpfr_sub_ui(mpfr_ptr, mpfr_srcptr, unsigned long, mpfr_rnd_t);
extern int mpfr_mul(mpfr_ptr, mpfr_srcptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_mul_ui(mpfr_ptr, mpfr_srcptr, unsigned long, mpfr_rnd_t);
extern int mpfr_mul_si(mpfr_ptr, mpfr_srcptr, long, mpfr_rnd_t);
extern int mpfr_div(mpfr_ptr, mpfr_srcptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_div_ui(mpfr_ptr, mpfr_srcptr, unsigned long, mpfr_rnd_t);
extern int mpfr_div_2ui(mpfr_ptr, mpfr_srcptr, unsigned long, mpfr_rnd_t);
extern int mpfr_sqr(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_neg(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_abs(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_sin(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_cos(mpfr_ptr, mpfr_srcptr, mpfr_rnd_t);
extern int mpfr_const_pi(mpfr_ptr, mpfr_rnd_t);
extern int mpfr_cmp(mpfr_srcptr, mpfr_srcptr);
extern int mpfr_cmp_si(mpfr_srcptr, long);
extern int mpfr_cmp_ui(mpfr_srcptr, unsigned long);
extern double mpfr_get_d(mpfr_srcptr, mpfr_rnd_t);
extern size_t __gmpfr_out_str(FILE*, int, size_t, mpfr_srcptr, mpfr_rnd_t);

typedef struct { mpfr_t lo, hi; } Ival;

static void iinit(Ival *x){ mpfr_init2(x->lo,PREC); mpfr_init2(x->hi,PREC); }
static void iclear(Ival *x){ mpfr_clear(x->lo); mpfr_clear(x->hi); }
static void iset_str(Ival *x,const char*s){
    if(mpfr_set_str(x->lo,s,10,MPFR_RNDD)!=0 || mpfr_set_str(x->hi,s,10,MPFR_RNDU)!=0){
        fprintf(stderr,"bad decimal: %s\n",s); exit(2);
    }
}
static void iset_si(Ival*x,long v){ mpfr_set_si(x->lo,v,MPFR_RNDD); mpfr_set_si(x->hi,v,MPFR_RNDU); }
static void iset_mp(Ival*x,mpfr_srcptr v){ mpfr_set(x->lo,v,MPFR_RNDD); mpfr_set(x->hi,v,MPFR_RNDU); }
static void icopy(Ival*out,const Ival*a){ mpfr_set(out->lo,a->lo,MPFR_RNDD); mpfr_set(out->hi,a->hi,MPFR_RNDU); }
static void iadd(Ival*out,const Ival*a,const Ival*b){
    mpfr_add(out->lo,a->lo,b->lo,MPFR_RNDD); mpfr_add(out->hi,a->hi,b->hi,MPFR_RNDU);
}
static void iadd_inplace(Ival*a,const Ival*b){
    mpfr_add(a->lo,a->lo,b->lo,MPFR_RNDD); mpfr_add(a->hi,a->hi,b->hi,MPFR_RNDU);
}
static void isub(Ival*out,const Ival*a,const Ival*b){
    mpfr_sub(out->lo,a->lo,b->hi,MPFR_RNDD); mpfr_sub(out->hi,a->hi,b->lo,MPFR_RNDU);
}
static void ineg(Ival*out,const Ival*a){
    mpfr_neg(out->lo,a->hi,MPFR_RNDD); mpfr_neg(out->hi,a->lo,MPFR_RNDU);
}

static mpfr_t TMP[16];
static void init_tmp(void){ for(int i=0;i<16;i++) mpfr_init2(TMP[i],PREC); }

static void imul(Ival*out,const Ival*a,const Ival*b){
    mpfr_mul(TMP[0],a->lo,b->lo,MPFR_RNDD);
    mpfr_mul(TMP[1],a->lo,b->hi,MPFR_RNDD);
    mpfr_mul(TMP[2],a->hi,b->lo,MPFR_RNDD);
    mpfr_mul(TMP[3],a->hi,b->hi,MPFR_RNDD);
    mpfr_set(TMP[4],TMP[0],MPFR_RNDD);
    for(int i=1;i<4;i++) if(mpfr_cmp(TMP[i],TMP[4])<0) mpfr_set(TMP[4],TMP[i],MPFR_RNDD);

    mpfr_mul(TMP[0],a->lo,b->lo,MPFR_RNDU);
    mpfr_mul(TMP[1],a->lo,b->hi,MPFR_RNDU);
    mpfr_mul(TMP[2],a->hi,b->lo,MPFR_RNDU);
    mpfr_mul(TMP[3],a->hi,b->hi,MPFR_RNDU);
    mpfr_set(TMP[5],TMP[0],MPFR_RNDU);
    for(int i=1;i<4;i++) if(mpfr_cmp(TMP[i],TMP[5])>0) mpfr_set(TMP[5],TMP[i],MPFR_RNDU);
    mpfr_set(out->lo,TMP[4],MPFR_RNDD); mpfr_set(out->hi,TMP[5],MPFR_RNDU);
}
static void idiv_pos(Ival*out,const Ival*a,const Ival*b){
    if(mpfr_cmp_si(b->lo,0)<=0){ fprintf(stderr,"nonpositive denominator\n"); exit(2); }
    mpfr_set_ui(TMP[0],1,MPFR_RNDN);
    Ival rec; iinit(&rec);
    mpfr_div(rec.lo,TMP[0],b->hi,MPFR_RNDD);
    mpfr_div(rec.hi,TMP[0],b->lo,MPFR_RNDU);
    imul(out,a,&rec); iclear(&rec);
}
static void iabs_upper(mpfr_ptr out,const Ival*a){
    mpfr_abs(TMP[0],a->lo,MPFR_RNDU); mpfr_abs(TMP[1],a->hi,MPFR_RNDU);
    if(mpfr_cmp(TMP[0],TMP[1])>=0) mpfr_set(out,TMP[0],MPFR_RNDU);
    else mpfr_set(out,TMP[1],MPFR_RNDU);
}
static void interval_trig_lipschitz(Ival*out,const Ival*z,int cosine){
    /* mid is inside [lo,hi]; rad covers both sides. */
    mpfr_add(TMP[0],z->lo,z->hi,MPFR_RNDN); mpfr_div_2ui(TMP[0],TMP[0],1,MPFR_RNDN);
    mpfr_sub(TMP[1],TMP[0],z->lo,MPFR_RNDU);
    mpfr_sub(TMP[2],z->hi,TMP[0],MPFR_RNDU);
    if(mpfr_cmp(TMP[2],TMP[1])>0) mpfr_set(TMP[1],TMP[2],MPFR_RNDU);
    if(cosine){ mpfr_cos(TMP[3],TMP[0],MPFR_RNDD); mpfr_cos(TMP[4],TMP[0],MPFR_RNDU); }
    else { mpfr_sin(TMP[3],TMP[0],MPFR_RNDD); mpfr_sin(TMP[4],TMP[0],MPFR_RNDU); }
    mpfr_sub(out->lo,TMP[3],TMP[1],MPFR_RNDD);
    mpfr_add(out->hi,TMP[4],TMP[1],MPFR_RNDU);
    if(mpfr_cmp_si(out->lo,-1)<0) mpfr_set_si(out->lo,-1,MPFR_RNDD);
    if(mpfr_cmp_si(out->hi,1)>0) mpfr_set_si(out->hi,1,MPFR_RNDU);
}

#define NFREE 71
#define NCP 75
#define NPV 3
#define KMAX 200

static const char *FREE_X[NFREE] = {
"5.9400000000000004",
"8.4574999999999996",
"12.375",
"15.5725",
"19.5425",
"26.995000000000001",
"34.174999999999997",
"34.18",
"38",
"41.744999999999997",
"45.899999999999999",
"53",
"53.104999999999997",
"60.340000000000003",
"64.420000000000002",
"65",
"71.974999999999994",
"79.125",
"83",
"91",
"95",
"102",
"103",
"114",
"117",
"121",
"122",
"133",
"136",
"140",
"155",
"159",
"167",
"174",
"178",
"186",
"193",
"197",
"205",
"212",
"216",
"224",
"231",
"242",
"245",
"254",
"265",
"273",
"280",
"284",
"291",
"292",
"299",
"303",
"310",
"311",
"318",
"322",
"329",
"337",
"341",
"348",
"356",
"360",
"367",
"374",
"375",
"382",
"383",
"397",
"398"
};
static const char *FREE_B[NFREE] = {
"0.00320898137883035788",
"0.00947716676721455134",
"0.00023623917604951465",
"0.00007520874009350037",
"0.00106850463847360668",
"0.00125894096724951332",
"0.00011928971464171382",
"0.00011630624759715705",
"0.00006082710141705064",
"0.00035450706289117359",
"0.00041978471449707422",
"0.00005580517071787396",
"0.00003138404717365566",
"0.00010052407579733559",
"0.00024089501391842097",
"0.00016180962490588125",
"0.00001491025201680857",
"0.00004873098508491933",
"0.00013611986202959102",
"0.00000135652127124763",
"0.00005172815189187196",
"0.00009512498508308942",
"0.00003658354556569053",
"0.00004741414362990623",
"0.00003474930599244032",
"0.0000681395979195147",
"0.0000167102129715996",
"0.00004268762990971669",
"0.00003377944713939387",
"0.00004902396887447235",
"0.00003174500808565188",
"0.00003491544346656961",
"0.00000810885941532138",
"0.00002896555123591228",
"0.0000243068574047461",
"0.00001047614814977361",
"0.000025702093168172",
"0.00001631855857211086",
"0.00001216129557674148",
"0.00002217641775748622",
"0.00001038446114534044",
"0.0000131283610364261",
"0.0000185788685694468",
"0.00000016136457488102",
"0.00000003256561011645",
"0.00000316670289308314",
"0.00001138133405786052",
"0.00000131619016773353",
"0.00000191831820004978",
"0.00001121457388715108",
"0.00000999546740254532",
"0.0000003283681732217",
"0.00000304294444731231",
"0.00001060292236724689",
"0.00000753392152659846",
"0.00000000322879210932",
"0.00000409567487280587",
"0.00000964299725552817",
"0.00000537195377905776",
"0.00000496624731422856",
"0.00000843899490030422",
"0.00000356389161218603",
"0.00000558721143225569",
"0.00000709505682570358",
"0.00000213739205609084",
"0.00000016065738713839",
"0.00000592705060390748",
"0.00000626790707041654",
"0.00000050020264025469",
"0.0000053298596445877",
"0.00000436744896005458"
};
static const char *FREE_L[NFREE] = {
"1.0232134761892537",
"0.47545380977460944",
"0.051029068938435077",
"0.034543809710818947",
"0.016893193069534525",
"0.010010794001700542",
"0.0014827210847833017",
"0.0025608671900736279",
"1.4917470401053701e-05",
"0.00038227635039500226",
"0.0012049405383510888",
"8.7910357173255534e-05",
"0.0008832209868291015",
"0.00034383986691820392",
"0.00011240038830668458",
"7.2871678715912236e-05",
"0.00028904930479931073",
"0.00016253082512145879",
"6.5886008666961597e-06",
"6.3596060538156931e-05",
"1.4839534649556998e-05",
"2.9672714809720265e-05",
"7.0823935591959032e-05",
"1.8785710235791177e-05",
"3.1837443583500552e-05",
"2.8127982547171005e-05",
"3.6438845075467516e-05",
"4.0232433174290834e-06",
"4.8963346587236258e-05",
"1.5004067048843405e-05",
"2.9546844225308707e-05",
"1.7479121666892462e-05",
"4.0264364360960829e-06",
"2.3507233045612854e-05",
"2.3934218361653478e-05",
"8.6457769990119461e-06",
"2.447705131552211e-05",
"3.7900161905633539e-05",
"2.2919605560024148e-05",
"4.2000590151968497e-05",
"7.6224058347691757e-05",
"0.00010523576977049533",
"0.0002166242041593806",
"0.0029889791442586442",
"0.0043501930176695252",
"0.00047764406011649527",
"0.00024771884394432991",
"0.00014372792882723771",
"3.6768650979342661e-05",
"9.7121704293915621e-05",
"5.5948721033354049e-05",
"4.1073477690160077e-05",
"2.7860503563566761e-05",
"2.9532654906182932e-05",
"2.6183480289757272e-05",
"2.3846906875803709e-05",
"1.9052873416070174e-05",
"1.8654418871598229e-05",
"1.5875306505249136e-05",
"1.7556219293212637e-05",
"1.7112723739970703e-05",
"1.080822678457108e-05",
"2.4286702516347508e-05",
"2.2981272974104525e-05",
"3.9742797222996101e-06",
"2.3039960317205226e-05",
"9.0933308675895247e-05",
"0.0001071888968369758",
"2.5276144286455085e-05",
"6.981273677090774e-05",
"3.9143350571426219e-05"
};
static const int CP_K[NCP] = { 35, 41, 47, 53, 59, 65, 71, 75, 76, 79, 80, 81, 82, 83, 88, 105, 111, 117, 124, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 145, 146, 147, 148, 151, 152, 153, 156, 157, 158, 159, 162, 163, 164, 167, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 186, 187, 188, 190, 191, 193, 194, 195, 197, 198, 199, 200 };
static const char *CP_L[NCP] = {
"8.0483437936688278e-05",
"7.4081503119542228e-05",
"4.4414365471911258e-05",
"3.5787629957091532e-05",
"3.8734041987965587e-05",
"5.5614817274239908e-05",
"0.00011862075710141405",
"0.00038636607748931159",
"0.0013098190606605053",
"0.0043478014283104272",
"0.0044799471997153941",
"0.0026730676995111134",
"0.0016847497400258153",
"0.00048343378846511418",
"0.00010782697143104767",
"2.0442137438942658e-05",
"2.6236210641789887e-05",
"6.29445343537367e-05",
"0.00011579042746368375",
"0.00021630252125895012",
"0.00086003363045564218",
"0.0017418870293609986",
"0.0026703968660603083",
"0.0033299547364493056",
"0.0035247462630035834",
"0.0032075825348193707",
"0.0025248864762126735",
"0.001707957813296794",
"0.00098081472889890694",
"0.0004658012055399606",
"0.00017691236420039",
"5.1466377760883879e-05",
"1.1995273901984504e-05",
"2.5580870510670899e-06",
"2.5951616964639938e-06",
"5.2882085887141833e-06",
"5.1562228790427162e-06",
"2.4956931185816405e-06",
"1.5575481734228751e-06",
"2.5003482981556161e-06",
"1.4583954221178471e-06",
"2.0686996729202279e-06",
"4.0482458234779938e-06",
"4.0691845424498863e-06",
"1.9164876722382915e-06",
"1.6817210963018953e-06",
"2.5737128748558615e-06",
"1.6319878619106116e-06",
"8.758634499026518e-07",
"2.1366692148386127e-05",
"0.00010685051136782204",
"0.00031014218702070297",
"0.00066544022900431529",
"0.0011544617211893091",
"0.0016901954102800862",
"0.0021360601132903263",
"0.0023555383612156016",
"0.0022719864440674032",
"0.0019051860508335935",
"0.0013657545312827232",
"0.00080740553345407277",
"0.00036361086263519477",
"9.9126816002530275e-05",
"2.5568693883899405e-05",
"3.1934919899743032e-05",
"1.5370099716969074e-05",
"1.3825448643791841e-05",
"6.8817318232383128e-05",
"9.6604143003667066e-05",
"0.00018034191603343876",
"0.00023843868383263927",
"1.2644843193996002e-05",
"1.5296140542250324e-05",
"1.4621149892951381e-05",
"1.3825737876798041e-05"
};
static const int PV_K[NPV] = { 191, 195, 200 };
static const char *PV_L[NPV] = {
"0.00015586889820022869",
"0.00027022536649247051",
"1.3543666387060414e-05"
};
static const char *T2_B = "0.66667154947916666667";
static const char *T2_L = "0.88380438360890146";
static const char *TARGET = "0.3805603";

static Ival C0,C2,PII;
static Ival FX[NFREE], FQ[NFREE], FD[NFREE], FP[NFREE];
static Ival MQ[KMAX+1], MD[KMAX+1], MP[KMAX+1];
static mpfr_t M1UP, M2UP;

static void init_constants(void){
    iinit(&C0); iinit(&C2); iinit(&PII); mpfr_init2(M1UP,PREC); mpfr_init2(M2UP,PREC);
    Ival lam,B,tmp,x,neg,ks,pi_k;
    iinit(&lam);iinit(&B);iinit(&tmp);iinit(&x);iinit(&neg);iinit(&ks);iinit(&pi_k);
    iset_si(&C0,1); iset_si(&C2,0);
    mpfr_const_pi(PII.lo,MPFR_RNDD); mpfr_const_pi(PII.hi,MPFR_RNDU);

    /* t^2 row and validity check. */
    iset_str(&lam,T2_L); iset_str(&B,T2_B);
    if(mpfr_cmp_si(lam.lo,0)<0){ fprintf(stderr,"negative t2 lambda\n"); exit(2); }
    mpfr_set_ui(TMP[0],2,MPFR_RNDN); mpfr_set_ui(TMP[1],3,MPFR_RNDN);
    mpfr_div(TMP[2],TMP[0],TMP[1],MPFR_RNDU);
    mpfr_set_ui(TMP[0],1,MPFR_RNDN); mpfr_set_ui(TMP[1],204800,MPFR_RNDN);
    mpfr_div(TMP[3],TMP[0],TMP[1],MPFR_RNDU);
    mpfr_add(TMP[4],TMP[2],TMP[3],MPFR_RNDU);
    if(mpfr_cmp(B.lo,TMP[4])<0){ fprintf(stderr,"t2 B not outward\n"); exit(2); }
    imul(&tmp,&lam,&B); iadd_inplace(&C0,&tmp);
    ineg(&C2,&lam);

    for(int i=0;i<NFREE;i++){ iinit(&FX[i]);iinit(&FQ[i]);iinit(&FD[i]);iinit(&FP[i]); }
    for(int k=0;k<=KMAX;k++){ iinit(&MQ[k]);iinit(&MD[k]);iinit(&MP[k]); iset_si(&MQ[k],0); }

    for(int i=0;i<NFREE;i++){
        iset_str(&x,FREE_X[i]); iset_str(&B,FREE_B[i]); iset_str(&lam,FREE_L[i]);
        if(mpfr_cmp_si(lam.lo,0)<0 || mpfr_cmp_si(x.lo,0)<=0){ fprintf(stderr,"bad free row\n"); exit(2); }
        /* Verify B >= (sin x / x)^2 using directed interval arithmetic. */
        interval_trig_lipschitz(&tmp,&x,0);
        idiv_pos(&neg,&tmp,&x); imul(&tmp,&neg,&neg);
        if(mpfr_cmp(B.lo,tmp.hi)<0){
            fprintf(stderr,"cos B not outward at row %d: B=%g need=%g\n",i,
                mpfr_get_d(B.lo,MPFR_RNDD),mpfr_get_d(tmp.hi,MPFR_RNDU)); exit(2);
        }
        imul(&tmp,&lam,&B); iadd_inplace(&C0,&tmp);
        icopy(&FX[i],&x);
        ineg(&FQ[i],&lam);              /* -lambda */
        imul(&FD[i],&lam,&x);           /* +lambda*x */
        idiv_pos(&tmp,&lam,&x); ineg(&FP[i],&tmp); /* -lambda/x */
    }

    /* Aggregate exact pi-mode coefficients. */
    for(int i=0;i<NPV;i++){
        iset_str(&lam,PV_L[i]);
        if(mpfr_cmp_si(lam.lo,0)<0){ fprintf(stderr,"negative parseval lambda\n"); exit(2); }
        iset_str(&B,"0.5"); imul(&tmp,&lam,&B); iadd_inplace(&C0,&tmp);
        for(int k=1;k<=PV_K[i];k++){ iadd(&tmp,&MQ[k],&lam); icopy(&MQ[k],&tmp); }
    }
    for(int i=0;i<NCP;i++){
        iset_str(&lam,CP_L[i]);
        if(mpfr_cmp_si(lam.lo,0)<0){ fprintf(stderr,"negative cos_pi lambda\n"); exit(2); }
        isub(&tmp,&MQ[CP_K[i]],&lam); icopy(&MQ[CP_K[i]],&tmp);
    }
    for(int k=1;k<=KMAX;k++){
        iset_si(&ks,k); imul(&pi_k,&PII,&ks);
        imul(&tmp,&MQ[k],&pi_k); ineg(&MD[k],&tmp); /* derivative coefficient -c*k*pi */
        idiv_pos(&MP[k],&MQ[k],&pi_k);              /* primitive c/(k*pi) */
    }

    /* Global M2 upper. */
    mpfr_set_ui(M2UP,0,MPFR_RNDU);
    iabs_upper(TMP[0],&C2); mpfr_mul_ui(TMP[0],TMP[0],2,MPFR_RNDU); mpfr_add(M2UP,M2UP,TMP[0],MPFR_RNDU);
    for(int i=0;i<NFREE;i++){
        iabs_upper(TMP[0],&FQ[i]); mpfr_sqr(TMP[1],FX[i].hi,MPFR_RNDU);
        mpfr_mul(TMP[2],TMP[0],TMP[1],MPFR_RNDU); mpfr_add(M2UP,M2UP,TMP[2],MPFR_RNDU);
    }
    for(int k=1;k<=KMAX;k++){
        iabs_upper(TMP[0],&MQ[k]); mpfr_mul_ui(TMP[1],PII.hi,k,MPFR_RNDU);
        mpfr_sqr(TMP[1],TMP[1],MPFR_RNDU); mpfr_mul(TMP[2],TMP[0],TMP[1],MPFR_RNDU);
        mpfr_add(M2UP,M2UP,TMP[2],MPFR_RNDU);
    }

    /* Global M1 upper bound for the cheap first sign test. */
    mpfr_set_ui(M1UP,0,MPFR_RNDU);
    iabs_upper(TMP[0],&C2); mpfr_mul_ui(TMP[0],TMP[0],4,MPFR_RNDU);
    mpfr_add(M1UP,M1UP,TMP[0],MPFR_RNDU);
    for(int i=0;i<NFREE;i++){
        iabs_upper(TMP[0],&FQ[i]); mpfr_mul(TMP[1],TMP[0],FX[i].hi,MPFR_RNDU);
        mpfr_add(M1UP,M1UP,TMP[1],MPFR_RNDU);
    }
    for(int k=1;k<=KMAX;k++){
        iabs_upper(TMP[0],&MQ[k]); mpfr_mul_ui(TMP[1],PII.hi,k,MPFR_RNDU);
        mpfr_mul(TMP[2],TMP[0],TMP[1],MPFR_RNDU); mpfr_add(M1UP,M1UP,TMP[2],MPFR_RNDU);
    }

    iclear(&lam);iclear(&B);iclear(&tmp);iclear(&x);iclear(&neg);iclear(&ks);iclear(&pi_k);
}

static Ival W[16];
static void init_workspace(void){ for(int i=0;i<16;i++) iinit(&W[i]); }

static void q_point_only(Ival*q, mpfr_srcptr tv){
    Ival *t=&W[0], *t2=&W[1], *arg=&W[2], *cv=&W[3], *term=&W[4], *theta=&W[5];
    iset_mp(t,tv); icopy(q,&C0);
    imul(t2,t,t); imul(term,&C2,t2); iadd_inplace(q,term);
    for(int i=0;i<NFREE;i++){
        imul(arg,&FX[i],t); interval_trig_lipschitz(cv,arg,1);
        imul(term,&FQ[i],cv); iadd_inplace(q,term);
    }
    imul(theta,&PII,t);
    for(int k=1;k<=KMAX;k++){
        mpfr_mul_ui(arg->lo,theta->lo,k,MPFR_RNDD);
        mpfr_mul_ui(arg->hi,theta->hi,k,MPFR_RNDU);
        interval_trig_lipschitz(cv,arg,1);
        imul(term,&MQ[k],cv); iadd_inplace(q,term);
    }
}

static void qp_point(Ival*qp, mpfr_srcptr tv){
    Ival *t=&W[0], *arg=&W[2], *sv=&W[3], *term=&W[4], *theta=&W[5];
    iset_mp(t,tv); iset_si(qp,0);
    imul(term,&C2,t);
    mpfr_mul_ui(term->lo,term->lo,2,MPFR_RNDD); mpfr_mul_ui(term->hi,term->hi,2,MPFR_RNDU);
    iadd_inplace(qp,term);
    for(int i=0;i<NFREE;i++){
        imul(arg,&FX[i],t); interval_trig_lipschitz(sv,arg,0);
        imul(term,&FD[i],sv); iadd_inplace(qp,term);
    }
    imul(theta,&PII,t);
    for(int k=1;k<=KMAX;k++){
        mpfr_mul_ui(arg->lo,theta->lo,k,MPFR_RNDD);
        mpfr_mul_ui(arg->hi,theta->hi,k,MPFR_RNDU);
        interval_trig_lipschitz(sv,arg,0);
        imul(term,&MD[k],sv); iadd_inplace(qp,term);
    }
}

static void primitive_point(Ival*out, mpfr_srcptr tv){
    Ival *t=&W[0], *t2=&W[1], *arg=&W[2], *sv=&W[3], *term=&W[4], *theta=&W[5], *t3=&W[6];
    iset_mp(t,tv); imul(out,&C0,t);
    imul(t2,t,t); imul(t3,t2,t); imul(term,&C2,t3);
    mpfr_div_ui(term->lo,term->lo,3,MPFR_RNDD); mpfr_div_ui(term->hi,term->hi,3,MPFR_RNDU);
    iadd_inplace(out,term);
    for(int i=0;i<NFREE;i++){
        imul(arg,&FX[i],t); interval_trig_lipschitz(sv,arg,0);
        imul(term,&FP[i],sv); iadd_inplace(out,term);
    }
    imul(theta,&PII,t);
    for(int k=1;k<=KMAX;k++){
        mpfr_mul_ui(arg->lo,theta->lo,k,MPFR_RNDD);
        mpfr_mul_ui(arg->hi,theta->hi,k,MPFR_RNDU);
        interval_trig_lipschitz(sv,arg,0);
        imul(term,&MP[k],sv); iadd_inplace(out,term);
    }
}

typedef struct { uint64_t j; uint16_t depth; } Cell;
typedef struct { uint64_t a,b; } Segment;
static int segcmp(const void*aa,const void*bb){
    const Segment*a=(const Segment*)aa; const Segment*b=(const Segment*)bb;
    return a->a<b->a?-1:(a->a>b->a?1:0);
}
static void unit_dyadic(mpfr_ptr out,uint64_t num,unsigned exp){
    mpfr_set_ui(out,num,MPFR_RNDN); mpfr_div_2ui(out,out,exp,MPFR_RNDN);
}

int main(int argc,char**argv){
    const int base_exp=9;       /* half-domain [0,2], initial width 2^-9 */
    const int initial=1024;
    int max_depth=22;
    uint64_t max_nodes=5000000;
    if(argc>1) max_depth=atoi(argv[1]);
    const char *target_s = argc>2 ? argv[2] : TARGET;
    if(max_depth<1 || max_depth>35){fprintf(stderr,"depth out of range\n");return 2;}

    init_tmp(); init_workspace(); init_constants();

    Ival q,qp,Pl,Pr; iinit(&q);iinit(&qp);iinit(&Pl);iinit(&Pr);
    mpfr_t mid,rad,left,right,qpabs,rem,tmp1,lower,upper,integral_half,terminal_half;
    mpfr_t integral,threshold,target,bound;
    mpfr_init2(mid,PREC);mpfr_init2(rad,PREC);mpfr_init2(left,PREC);mpfr_init2(right,PREC);
    mpfr_init2(qpabs,PREC);mpfr_init2(rem,PREC);mpfr_init2(tmp1,PREC);mpfr_init2(lower,PREC);
    mpfr_init2(upper,PREC);mpfr_init2(integral_half,PREC);mpfr_init2(terminal_half,PREC);
    mpfr_init2(integral,PREC);mpfr_init2(threshold,PREC);mpfr_init2(target,PREC);mpfr_init2(bound,PREC);
    mpfr_set_ui(integral_half,0,MPFR_RNDU); mpfr_set_ui(terminal_half,0,MPFR_RNDU);
    if(mpfr_set_str(target,target_s,10,MPFR_RNDU)!=0 || mpfr_cmp_si(target,0)<=0){
        fprintf(stderr,"invalid positive target\n"); return 2;
    }
    mpfr_set_ui(tmp1,1,MPFR_RNDN); mpfr_div(threshold,tmp1,target,MPFR_RNDD);

    size_t cap=8192,top=0,scap=8192,sn=0;
    Cell*stack=(Cell*)malloc(cap*sizeof(Cell)); Segment*segments=(Segment*)malloc(scap*sizeof(Segment));
    if(!stack||!segments){fprintf(stderr,"alloc failed\n");return 2;}
    for(int j=0;j<initial;j++) stack[top++]=(Cell){(uint64_t)j,0};

    uint64_t nodes=0,pos=0,neg=0,term=0,local_deriv=0;
    while(top){
        Cell cell=stack[--top]; nodes++;
        if(nodes>max_nodes){fprintf(stderr,"FAIL max_nodes\n");return 2;}
        unsigned dexp=(unsigned)(base_exp+cell.depth);
        unit_dyadic(mid,2*cell.j+1,dexp+1);
        mpfr_set_ui(rad,1,MPFR_RNDN); mpfr_div_2ui(rad,rad,dexp+1,MPFR_RNDN);
        q_point_only(&q,mid);

        /* Cheap global-Lipschitz test. */
        mpfr_mul(rem,M1UP,rad,MPFR_RNDU);
        mpfr_sub(lower,q.lo,rem,MPFR_RNDD); mpfr_add(upper,q.hi,rem,MPFR_RNDU);

        if(mpfr_cmp_si(upper,0)>0 && mpfr_cmp_si(lower,0)<0){
            /* Sharpen only ambiguous cells with q'(mid) and M2. */
            qp_point(&qp,mid); local_deriv++;
            iabs_upper(qpabs,&qp); mpfr_mul(rem,qpabs,rad,MPFR_RNDU);
            mpfr_sqr(tmp1,rad,MPFR_RNDU); mpfr_mul(tmp1,tmp1,M2UP,MPFR_RNDU);
            mpfr_div_2ui(tmp1,tmp1,1,MPFR_RNDU); mpfr_add(rem,rem,tmp1,MPFR_RNDU);
            mpfr_sub(lower,q.lo,rem,MPFR_RNDD); mpfr_add(upper,q.hi,rem,MPFR_RNDU);
        }

        if(mpfr_cmp_si(upper,0)<=0){neg++;continue;}
        if(mpfr_cmp_si(lower,0)>=0){
            uint64_t scale=((uint64_t)1)<<(max_depth-cell.depth);
            if(sn==scap){scap*=2;segments=(Segment*)realloc(segments,scap*sizeof(Segment));if(!segments)return 2;}
            segments[sn++]=(Segment){cell.j*scale,(cell.j+1)*scale}; pos++;continue;
        }
        if(cell.depth>=max_depth){
            mpfr_set_ui(tmp1,1,MPFR_RNDN); mpfr_div_2ui(tmp1,tmp1,dexp,MPFR_RNDN);
            mpfr_mul(tmp1,tmp1,upper,MPFR_RNDU); mpfr_add(terminal_half,terminal_half,tmp1,MPFR_RNDU);
            term++;continue;
        }
        if(top+2>cap){cap*=2;stack=(Cell*)realloc(stack,cap*sizeof(Cell));if(!stack)return 2;}
        stack[top++]=(Cell){2*cell.j+1,(uint16_t)(cell.depth+1)};
        stack[top++]=(Cell){2*cell.j,(uint16_t)(cell.depth+1)};
    }

    /* Merge positive dyadic cells, then integrate each component once. */
    qsort(segments,sn,sizeof(Segment),segcmp);
    uint64_t denom_exp=(uint64_t)(base_exp+max_depth);
    size_t components=0;
    for(size_t i=0;i<sn;){
        uint64_t a=segments[i].a,b=segments[i].b; i++;
        while(i<sn && segments[i].a<=b){ if(segments[i].b>b)b=segments[i].b; i++; }
        unit_dyadic(left,a,(unsigned)denom_exp); unit_dyadic(right,b,(unsigned)denom_exp);
        primitive_point(&Pl,left); primitive_point(&Pr,right);
        mpfr_sub(tmp1,Pr.hi,Pl.lo,MPFR_RNDU); mpfr_add(integral_half,integral_half,tmp1,MPFR_RNDU);
        components++;
    }
    mpfr_add(integral_half,integral_half,terminal_half,MPFR_RNDU);
    mpfr_mul_ui(integral,integral_half,2,MPFR_RNDU); /* even q */
    mpfr_set_ui(tmp1,1,MPFR_RNDN); mpfr_div(bound,tmp1,integral,MPFR_RNDD);
    int pass=mpfr_cmp(integral,threshold)<0;

    mpfr_sub(tmp1,threshold,integral,MPFR_RNDD);

    printf("%s\n",pass?"PASS":"FAIL");
    printf("precision_bits=%d\n",PREC);
    printf("target_exact=%s\n",target_s);
    printf("target_binary64_diagnostic=%.17g\n",mpfr_get_d(target,MPFR_RNDN));
    printf("integral_upper_mpfr="); __gmpfr_out_str(stdout,10,0,integral,MPFR_RNDU); printf("\n");
    printf("threshold_lower_mpfr="); __gmpfr_out_str(stdout,10,0,threshold,MPFR_RNDD); printf("\n");
    printf("implied_bound_lower_mpfr="); __gmpfr_out_str(stdout,10,0,bound,MPFR_RNDD); printf("\n");
    printf("D_margin_lower_mpfr="); __gmpfr_out_str(stdout,10,0,tmp1,MPFR_RNDD); printf("\n");
    printf("integral_upper_binary64_diagnostic=%.17g\n",mpfr_get_d(integral,MPFR_RNDU));
    printf("threshold_lower_binary64_diagnostic=%.17g\n",mpfr_get_d(threshold,MPFR_RNDD));
    printf("implied_bound_lower_binary64_diagnostic=%.17g\n",mpfr_get_d(bound,MPFR_RNDD));
    printf("D_margin_lower_binary64_diagnostic=%.17g\n",mpfr_get_d(tmp1,MPFR_RNDD));
    printf("M1_upper=%.17g M2_upper=%.17g\n",mpfr_get_d(M1UP,MPFR_RNDU),mpfr_get_d(M2UP,MPFR_RNDU));
    printf("nodes=%llu positive_cells=%llu negative_cells=%llu terminal=%llu local_derivative=%llu components=%zu depth=%d\n",
        (unsigned long long)nodes,(unsigned long long)pos,(unsigned long long)neg,
        (unsigned long long)term,(unsigned long long)local_deriv,components,max_depth);

    fflush(stdout);
    _Exit(pass?0:1);
}
