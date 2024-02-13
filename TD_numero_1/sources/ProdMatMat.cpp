#include <algorithm>
#include <cassert>
#include <iostream>
#include <thread>
#if defined(_OPENMP)
#include <omp.h>
#endif
#include "ProdMatMat.hpp"

namespace {
void prodSubBlocks(int iRowBlkA, int iColBlkB, int iColBlkA, int szBlock,
                   const Matrix& A, const Matrix& B, Matrix& C) {
      for (int j = iColBlkB; j < std::min(B.nbCols, iColBlkB + szBlock); j++)
        for (int k = iColBlkA; k < std::min(A.nbCols, iColBlkA + szBlock); k++)  
          for (int i = iRowBlkA; i < std::min(A.nbRows, iRowBlkA + szBlock); ++i)
            C(i, j) += A(i, k) * B(k, j);
    }
}

// namespace

Matrix operator*(const Matrix& A, const Matrix& B) {
  Matrix C(A.nbRows, B.nbCols, 0.0);
  const int szBlock = 128;
  // prodSubBlocks(0, 0, 0, std::max({A.nbRows, B.nbCols, A.nbCols}), A, B, C);
  for (int l = 0; l < B.nbCols + szBlock; l += szBlock)
    for (int m=0; m<B.nbCols; m+= szBlock)
      for (int n=0; n < A.nbCols; n+= szBlock)
        prodSubBlocks(l, m, n, szBlock, A, B, C);
  return C;
}
