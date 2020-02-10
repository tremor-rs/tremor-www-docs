# Security

The tremor project follows strict coding practices that help to reduce the incidence,
surface and likelihood of direct or indirect security risks to users of the software.

Specifically:

  * Tremor favors safe over unsafe rust code.
    * Safe code is generally considered the better option
    * Unless, performance critical concerns on the hot path suggest otherwise
    * Over time, unsafe code should be displaced with safe code
  * Tremor is conservative on matters of code health.
    * Clippy is pedantic mode is mandated for all rust code
    * Property based testing, model-based testing and fuzz-testing are used
    * Additional audits for code quality are in force
  * Static analysis
    * Tremor analyses external library dependencies for all direct and indirect dependencies
    * Tremor logs and reports all LICENSE, CVE and other violations both in our CI code and using other tools
    * Additional dynamic and static analysis methods can be added to broaden/deepen coverage


# Non Recommendation

We do *not* recommend running tremor outside of corporate firewalls at this time.

Although every care is taken to ensure there are no security flaws within the code-base
tremor, to date, has been designed with deployment in secure, well-defended environments
with active intrusion detection and defenses run by security professionals.


# Recommendation

We do recommend running tremor in secured environments following the best practices of
the organization and deployment platform. For example, the security blueprints for deploying
secure services to Amazon's infrastructure should be followed when deploying to AWS. The
security blueprints for the Google Cloud Platform should be followed when deploying to GCP.

Where tremor is deployed into bespoke bare metal data centers, tremor should be treated as
software that is not secure in and of itself. A secured environment should be provided for
it to run within.

# Future

Contributions to tremor security are very welcome, highly encouraged and we would be
delighted to accept contributions that move our security roadmap priority.
