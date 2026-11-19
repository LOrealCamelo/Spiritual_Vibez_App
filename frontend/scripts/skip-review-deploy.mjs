// This audit branch is for tests and review only. Exit 0 tells Netlify to
// cancel before building; production main and other branches keep their policy.
const branches=[process.env.BRANCH,process.env.HEAD,process.env.COMMIT_REF];
const review=branches.some(value=>value==='review/prelaunch-audit'||value==='feature/manual-memberships'||value==='feature/neon-postgres-memberships'||value==='release/neon-memberships-review'||value==='fix/stripe-restricted-live-keys');
console.log(review?'Review-only branch: skip Netlify deploy.':'Use the existing build policy.');
process.exit(review?0:1);
