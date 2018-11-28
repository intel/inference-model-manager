## Helm deployment of Dex

### Preparation to installation

You have to set all values specify in this chapter to properly run this chart
```issuer: "none" - issuer must be the same like in dex config
   config:
     <There you can put your dex config>
   resources: {} - it`s optionall, if you want you can specify resources for dex
```

Inference Model Manager requires TSL for internal traffic. We recommend to use for this purpose our script ```generate-dex-certs.sh``` located in ```certs``` directory.
Before running the script mentioned above, set the environment variable ```DEX_NAMESPACE```


### Installation

To install this chart after preparation phase use:
```helm install .```
