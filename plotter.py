import mplfinance as mpf


def mpf_plot(df, quotation, resistance, support,
             threshold, volume_flag):
    def levels_text_create(levels):
        tx = ''
        if len(levels) == 0:
            tx = 'resistances not found'
        else:
            for lv in levels:
                tx = tx + ' ' + str(lv.round(4))
        return tx

    resistance_tx = levels_text_create(resistance)
    support_tx = levels_text_create(support)

    tx = (quotation + '  ' + str(df.index[0]) + ' - ' + str(df.index[-1]) + '\n' +
          'th = ' + str(threshold) + ' | ' +  '\n' +
          #'max_diff = ' + str(diff_percent.round(5)) + '%' + ' | ' + 
          #'eps = ' + str(eps.round(5)) + ' | ' + 
          #'cluster numbers = ' + str(cluster_numbers) + '\n' + 
          'resistances: ' + resistance_tx + '\n' + 
          'supports: ' + support_tx
         )
    
    levels =  resistance + support
    colors = tuple(['r'] * len(resistance) + ['g'] * len(support))

    hlines_config = dict(hlines=levels, 
                         colors=colors, 
                         linewidths=1
                        )
    tittle_config = dict(title = tx, y = 1, x = 0.11,
                         fontsize = 10, fontweight = 10,
                         ha = 'left')
    save_config = dict(fname = 'images/' + quotation + '.png',
                       transparent = False)

    mpf.plot(df, type='candle', volume=volume_flag, style='yahoo',
             figratio=(16,8), xrotation=0, figscale=1,
             hlines=hlines_config,
             title=tittle_config,
             savefig=save_config,
             tight_layout=True
            )