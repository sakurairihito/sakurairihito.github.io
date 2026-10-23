function c = pagemtimes(a, b)
% Two-input, at-most-3D subset used by Chebfun3/feval at the pinned revision.
% Implements C(:,:,k) = A(:,:,k)*B(:,:,k), including singleton pages.
% This is an Octave adapter, not a complete replacement for MATLAB pagemtimes.
  assert(ndims(a) <= 3 && ndims(b) <= 3, 'Only up to 3D inputs are supported.');
  assert(size(a, 2) == size(b, 1), 'Inner matrix dimensions must agree.');
  na = size(a, 3);
  nb = size(b, 3);
  assert(na == nb || na == 1 || nb == 1, 'Page dimensions must agree.');
  c = zeros(size(a, 1), size(b, 2), max(na, nb));
  for k = 1:max(na, nb)
    c(:, :, k) = a(:, :, min(k, na)) * b(:, :, min(k, nb));
  end
end
