function run_chebfun_spread(chebfun_dir, output_dir)
% Reproduce the BlackScholes2D example with a pinned, unmodified Chebfun.
% MATLAB: run_chebfun_spread('/path/to/chebfun', '/path/to/new_output')
% Octave: the adjacent octave_compat directory supplies the one missing call.
  if exist(output_dir, 'dir')
    error('Choose a new output directory; existing results are preserved.');
  end
  addpath(chebfun_dir);
  here = fileparts(mfilename('fullpath'));
  if exist('OCTAVE_VERSION', 'builtin')
    addpath(fullfile(here, 'octave_compat'));
    test_compat();
  end
  rng(0, 'twister');
  smoke = chebfun3(@(x,y,z) 1+x.*y+z.^2, 'eps', 1e-12);
  p = [-.7; .2; .8];
  assert(max(abs(smoke(p,p,p)-(1+2*p.^2))) < 1e-10);
  mkdir(output_dir);
  diary(fullfile(output_dir, 'run.txt'));

  % The article integrates log returns in [-10,10]^2 using 150 nodes/axis.
  [nodes, weights] = chebpts(150, [-10, 10]);
  assert(abs(sum(weights)-20) < 1e-12);
  assert(abs(weights*(nodes.^2)-2000/3) < 1e-10);
  [x, y] = meshgrid(nodes, nodes);
  calls = 0;
  dom = [.3, 2, .3, 2, -.9, .9];
  [tt, kk, rr] = ndgrid(linspace(.3,2,15), linspace(.3,2,15), linspace(-.9,.9,15));
  rng(20261020, 'twister');
  random_points = [.3+1.7*rand(500,1), .3+1.7*rand(500,1), -.9+1.8*rand(500,1)];
  tic;
  direct = arrayfun(@price, tt, kk, rr);
  direct_time = toc;
  random_direct = arrayfun(@price, random_points(:,1), random_points(:,2), random_points(:,3));
  dlmwrite(fullfile(output_dir, 'quadrature.csv'), [nodes weights'], 'precision', 17);
  dlmwrite(fullfile(output_dir, 'grid_direct.csv'), [tt(:) kk(:) rr(:) direct(:)], 'precision', 17);
  dlmwrite(fullfile(output_dir, 'random_direct.csv'), [random_points random_direct], 'precision', 17);

  modes = {'classic', 'default'};
  results = struct();
  results.runtime = version;
  results.domain = dom;
  results.quadrature_nodes = 150;
  results.tolerance = 1e-5;
  results.construction_rng_seed = 0;
  results.validation_rng_seed = 20261020;
  results.direct_grid_seconds = direct_time;
  for m = 1:numel(modes)
    mode = modes{m};
    rng(0, 'twister');
    calls = 0;
    fprintf('Constructing %s Chebfun3...\n', mode);
    tic;
    if strcmp(mode, 'classic')
      f = chebfun3(@price, 'eps', 1e-5, 'vectorize', dom, 'classic');
    else
      f = chebfun3(@price, 'eps', 1e-5, 'vectorize', dom);
    end
    construction_seconds = toc;
    construction_calls = calls;
    [rank_t, rank_k, rank_r] = rank(f);
    [length_t, length_k, length_r] = length(f);
    % One warm-up, then the median of five grid evaluations.
    feval(f, tt, kk, rr);
    eval_seconds = zeros(5,1);
    for repeat = 1:5
      tic;
      approx = f(tt, kk, rr);
      eval_seconds(repeat) = toc;
    end
    random_approx = f(random_points(:,1), random_points(:,2), random_points(:,3));
    s = struct('ranks', [rank_t rank_k rank_r], ...
      'lengths', [length_t length_k length_r], ...
      'construction_seconds', construction_seconds, ...
      'construction_price_calls', construction_calls, ...
      'grid_evaluation_seconds', median(eval_seconds), ...
      'grid_evaluation_repeats_seconds', eval_seconds', ...
      'grid_max_abs_vs_quadrature', max(abs(approx(:)-direct(:))), ...
      'random_max_abs_vs_quadrature', max(abs(random_approx-random_direct)));
    results.(mode) = s;
    dlmwrite(fullfile(output_dir, [mode '_grid.csv']), [tt(:) kk(:) rr(:) approx(:)], 'precision', 17);
    dlmwrite(fullfile(output_dir, [mode '_random.csv']), [random_points random_approx], 'precision', 17);
    core = f.core;
    t_coeffs = chebcoeffs(f.cols);
    k_coeffs = chebcoeffs(f.rows);
    rho_coeffs = chebcoeffs(f.tubes);
    % Chebfun stores endpoint values separately from polynomial coefficients.
    % With relaxed eps these can differ, so export both for exact replay.
    t_endpoints = f.cols([dom(1); dom(2)]);
    k_endpoints = f.rows([dom(3); dom(4)]);
    rho_endpoints = f.tubes([dom(5); dom(6)]);
    save(fullfile(output_dir, [mode '_coefficients.mat']), 'core', 't_coeffs', 'k_coeffs', ...
      'rho_coeffs', 't_endpoints', 'k_endpoints', 'rho_endpoints', '-v7');
    fprintf('%s: ranks %d/%d/%d, lengths %d/%d/%d, max grid error %.9g\n', ...
      mode, s.ranks, s.lengths, s.grid_max_abs_vs_quadrature);
    fid = fopen(fullfile(output_dir, 'chebfun_results.json'), 'w');
    fprintf(fid, '%s\n', jsonencode(results));
    fclose(fid);
  end
  diary off;

  function v = price(t, strike, correlation)
    calls = calls + 1;
    variance = .3^2*t;
    mu = -.5*variance;
    normalizer = 2*pi*variance*sqrt(1-correlation^2);
    exponent = -((x-mu).^2 - 2*correlation*(x-mu).*(y-mu) + ...
      (y-mu).^2)/(2*variance*(1-correlation^2));
    values = max(exp(x)-exp(y)-strike, 0) .* exp(exponent)/normalizer;
    v = weights*values*weights';
  end
end
