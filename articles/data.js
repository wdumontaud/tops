// articles/data.js — publications à afficher sur la page articles.
// Champs : year, title, authors, venue (revue/conférence), type ('journal'|'conference'|'preprint'),
// status ('published'|'in-press'|'preprint'), doi, hal, links [{label,url}], abstract (optionnel).
const ARTICLES=[
  {
    year:2026, type:'journal', status:'published',
    title:'A novel 2D diffusion model for composite domain with non-regularly shaped interface',
    authors:'William Dumontaud, Julien Berger, Benjamin Kadoch',
    venue:'Computers & Mathematics with Applications, 217, pp. 444–469',
    doi:'10.1016/j.camwa.2026.06.007', hal:'https://hal.science/hal-05679840',
    links:[{label:'SSRN (preprint)', url:'https://papers.ssrn.com/abstract=5369908'}],
    abstract:'This paper presents a new two-dimensional transient diffusion model adapted to composite domains with non-regular internal interfaces. The model employs a finite difference approach based on the explicit DuFort–Frankel scheme, coupled with the Ghost Fluid Method, to ensure both numerical efficiency and accurate interface treatment. The numerical scheme is first validated against an analytical solution, demonstrating second-order accuracy in both space and time, then against a finite element model under realistic thermal boundary conditions relevant to building physics. The model is subsequently applied to the optimization of the interface geometry between two materials in a building wall exposed to spatially heterogeneous conditions typical of an urban canyon environment.'
  },
  {
    year:2026, type:'journal', status:'published',
    title:'Numerical framework for optimizing the thermal performance of building walls with shaped interfaces between material layers',
    authors:'William Dumontaud, Julien Berger, Benjamin Kadoch',
    venue:'Journal of Building Performance Simulation, pp. 1–22',
    doi:'10.1080/19401493.2026.2714908', hal:'https://hal.science/hal-05734832'
  },
  {
    year:2026, type:'journal', status:'published',
    title:'Similarity laws for experimental assessment of the thermal efficiency of a wall with optimized shape submitted to two-dimensional heat transfer',
    authors:'Julien Berger, William Dumontaud, Armelle Nouviaire, Sultan Alpar, Benjamin Kadoch',
    venue:'Journal of Building Physics, 50 (3), pp. 471–499',
    doi:'10.1177/17442591261461693', hal:'https://hal.science/hal-05855166'
  },
  {
    year:2026, type:'preprint', status:'preprint',
    title:'Stable explicit scheme for two-dimensional heat transfer problem in non-cartesian domain',
    authors:'Julien Berger, William Dumontaud, Benjamin Kadoch',
    venue:'SSRN preprint, posted 7 Apr 2026',
    doi:'10.2139/ssrn.6532379',
    links:[{label:'SSRN', url:'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6532379'}],
    abstract:'This paper investigates the numerical solution of diffusion problems in non-Cartesian domains using finite differences. A coordinate transformation is employed to perform computations on a regular structured grid, but it modifies the governing equation to a hyperbolic-type operator and strongly affects the stability of explicit schemes. To address this issue, Super Time-Stepping (STS) methods are considered, focusing on the RKL and RKG schemes. A rigorous theoretical framework is developed to derive stability conditions linking the number of stages, the spatial mesh size and the superstep.'
  },
  {
    year:2026, type:'conference', status:'published',
    title:'Design optimization of the insulation domain in building wall',
    authors:'William Dumontaud, Julien Berger, Benjamin Kadoch, Walter Mazuroski',
    venue:'18th International Heat Transfer Conference (IHTC-18), Rio de Janeiro, Brazil, Aug 2026',
    hal:'https://hal.science/hal-05761716',
    links:[{label:'Poster IHTC-18', url:'https://wdumontaud.github.io/poster_ihtc2026/anim0.html'}]
  },
  {
    year:2025, type:'conference', status:'published',
    title:'Design de l’isolation des parois pour améliorer l’efficacité énergétique',
    authors:'William Dumontaud, Julien Berger, Benjamin Kadoch',
    venue:'33ème Congrès Français de Thermique (SFT 2025), Chambéry, France, Jun 2025',
    hal:'https://hal.science/hal-05141125'
  },
];
