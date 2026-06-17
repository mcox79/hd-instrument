import torch
N=1024
def mk_sparse(M,fk,g):
    k=max(1,round(fk*N)); keys=torch.zeros((M,N))
    signs=(torch.randint(0,2,(M,k),generator=g).float()*2-1)
    idx=torch.argsort(torch.rand((M,N),generator=g),dim=1)[:,:k]
    keys.scatter_(1,idx,signs); return keys
def mk_dense(M,g): return (torch.randint(0,2,(M,N),generator=g).float()*2-1)
def exact(rec,val):
    dot=(rec*val).sum(1); nrm=rec.norm(dim=1)*val.norm(dim=1)+1e-12
    return float(((dot/nrm)>=0.90).float().mean())
def softmax_recall_chunked(keys,vals,beta,cosine=False,B=512):
    M=keys.shape[0]; K=keys
    if cosine: K=keys/(keys.norm(dim=1,keepdim=True)+1e-12)
    recs=[]
    for i in range(0,M,B):
        q=K[i:i+B]
        sc=q@K.t()
        w=torch.softmax(beta*sc,dim=1)
        recs.append(torch.sign(w@vals))
    return torch.cat(recs,0)
print("=== RAW-DOT softmax (beta=1.0): dense f_k=1.0 vs sparse f_k=0.05 ===")
for M in [4096,8192,16384]:
    g=torch.Generator().manual_seed(7)
    kd=mk_dense(M,g); vd=mk_dense(M,g); rd=softmax_recall_chunked(kd,vd,1.0)
    g2=torch.Generator().manual_seed(7)
    ks=mk_sparse(M,0.05,g2); vs=mk_dense(M,g2); rs=softmax_recall_chunked(ks,vs,1.0)
    print(f"  M={M:6d}  dense={exact(rd,vd):.3f}  sparse={exact(rs,vs):.3f}")
print("=== COSINE-normalized softmax (beta sweep) at M=4096: does a discriminating regime appear? ===")
for beta in [5.0,20.0,50.0,100.0]:
    g=torch.Generator().manual_seed(7); kd=mk_dense(4096,g); vd=mk_dense(4096,g)
    rd=softmax_recall_chunked(kd,vd,beta,cosine=True)
    g2=torch.Generator().manual_seed(7); ks=mk_sparse(4096,0.05,g2); vs=mk_dense(4096,g2)
    rs=softmax_recall_chunked(ks,vs,beta,cosine=True)
    print(f"  beta={beta:6.1f}  dense={exact(rd,vd):.3f}  sparse={exact(rs,vs):.3f}")
