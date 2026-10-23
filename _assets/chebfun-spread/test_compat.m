function test_compat()
  addpath(fullfile(fileparts(mfilename('fullpath')), 'octave_compat'));
  a = reshape(1:24, 2, 3, 4);
  b = reshape(1:12, 3, 1, 4);
  c = pagemtimes(a, b);
  assert(isequal(size(c), [2, 1, 4]));
  for k = 1:4
    assert(isequal(c(:, :, k), a(:, :, k) * b(:, :, k)));
  end
  c = pagemtimes(a(:, :, 1), b);
  for k = 1:4
    assert(isequal(c(:, :, k), a(:, :, 1) * b(:, :, k)));
  end
  c = pagemtimes(a, b(:, :, 1));
  for k = 1:4
    assert(isequal(c(:, :, k), a(:, :, k) * b(:, :, 1)));
  end
  assert(isequal(pagemtimes(2, 3), 6));
  fprintf('Page multiplication checks passed.\n');
end
