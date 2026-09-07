# Signal comparison subsection for Results

## 6.6 Standard and label-aware signals capture different failure modes

The previous sections show that high-impact perturbations may remain weakly observable under the aggregate stealth metric. To understand which audit signals contribute to this effect, we compare two groups of detectability signals. The first group contains the standard feature/score-based integrity signals: feature-distribution JSD, MMD, KS rejection rate, and score-drift JSD. The second group contains label-aware and prediction-aware signals: label-prior shift, label JSD, predicted-positive-rate shift, prediction disagreement, prediction JSD, and confusion-profile shifts.

The comparison reveals that the auditability gap is not caused by a single uniformly weak detector. Instead, different perturbation families are captured by different signal groups.

For ID target-shift perturbations, the standard detectability score is zero on average, while the label/prediction-aware signal group reaches an average detectability of 0.174 and the full detectability score reaches 0.111. This confirms that feature/score-centric signals are insufficient for target-shift-like perturbations, especially prior-preserving label flips. These attacks can affect benchmark conclusions while leaving little or no trace in conventional feature-centric integrity checks.

For corruption attacks, the new signal group also improves observability. The standard detectability score is 0.190 on average, while the label/prediction-aware signal group reaches 0.323 and the full detectability score reaches 0.275. This indicates that prediction-aware signals are useful not only for label perturbations, but also for structured feature corruptions that change model behaviour.

In contrast, covariate-shift perturbations are better captured by the standard feature-centric signals. Under ID covariate shift, the standard detectability score reaches 0.658, while the label/prediction-aware signal group reaches only 0.147. This suggests that feature-distribution and statistical integrity signals remain essential for detecting distributional changes in the input space.

These results support a signal-family interpretation of auditability. No single signal group dominates across all perturbation types. Feature-centric signals are effective for covariate shift, whereas label-aware and prediction-aware signals are necessary to expose target-shift and some corruption-induced behavioural changes. Therefore, robust benchmark auditing should report detectability by signal family rather than relying only on a single aggregate drift or integrity score.

This analysis strengthens the central claim of the paper: the auditability gap is not merely a matter of model robustness, but also a matter of signal design. Perturbations become especially problematic when the benchmark monitors the wrong observability channel for the type of failure being induced.
